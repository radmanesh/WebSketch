import { PlacedComponent } from '@/types/types';
import { componentRegistry } from './componentRegistry';
import { getRendererConfig, defaultWireframeConfig, WireframeConfig, hasBorder } from './config';
import { WireframeStructure, WireframeElement, RendererConfig, ComponentType } from './types';
import { BaseRenderer } from './renderers/BaseRenderer';

/**
 * Main wireframe generator class
 * Orchestrates rendering of components into wireframe structure
 */
export class WireframeGenerator {
  private config: WireframeConfig;

  constructor(config: Partial<WireframeConfig> = {}) {
    this.config = { ...defaultWireframeConfig, ...config };
  }

  /**
   * Generate wireframe structure from components
   */
  generate(components: PlacedComponent[]): WireframeStructure {
    if (components.length === 0) {
      return {
        width: this.config.padding * 2,
        height: this.config.padding * 2,
        elements: [],
        config: this.config,
      };
    }

    // Calculate bounding box
    const bounds = this.calculateBounds(components);
    const width = bounds.width + this.config.padding * 2;
    const height = bounds.height + this.config.padding * 2;
    const offsetX = -bounds.minX + this.config.padding;
    const offsetY = -bounds.minY + this.config.padding;

    // Render all components
    const elements: WireframeElement[] = [];

    for (const component of components) {
      const componentElements = this.renderComponent(component, offsetX, offsetY);
      elements.push(...componentElements);
    }

    return {
      width,
      height,
      elements,
      config: this.config,
    };
  }

  /**
   * Calculate bounding box of all components
   */
  private calculateBounds(components: PlacedComponent[]): {
    minX: number;
    minY: number;
    maxX: number;
    maxY: number;
    width: number;
    height: number;
  } {
    let minX = Infinity;
    let minY = Infinity;
    let maxX = -Infinity;
    let maxY = -Infinity;

    for (const component of components) {
      minX = Math.min(minX, component.x);
      minY = Math.min(minY, component.y);
      maxX = Math.max(maxX, component.x + component.width);
      maxY = Math.max(maxY, component.y + component.height);
    }

    return {
      minX,
      minY,
      maxX,
      maxY,
      width: maxX - minX,
      height: maxY - minY,
    };
  }

  /**
   * Render a single component into wireframe elements
   */
  private renderComponent(
    component: PlacedComponent,
    offsetX: number,
    offsetY: number
  ): WireframeElement[] {
    // Get renderer for component type
    const renderer = componentRegistry.getRenderer(component.type);
    if (!renderer) {
      console.warn(`No renderer found for component type: ${component.type}`);
      return [];
    }

    // Validate component if renderer has validation
    if (renderer.validate && !renderer.validate(component)) {
      console.warn(`Component ${component.id} failed validation`);
      return [];
    }

    // Get renderer configuration
    const rendererConfig = getRendererConfig(component.type, this.config);
    const fullConfig: RendererConfig = {
      ...rendererConfig,
      componentDetails: this.config.componentDetails?.[component.id],
    };

    // Render component content
    const contentElements = renderer.render(component, fullConfig);

    // Create component group with container rectangle
    const componentElements: WireframeElement[] = [];

    // Only add container rectangle with border for components that should have borders
    // No fill - all components are transparent in export
    if (fullConfig.hasBorder && component.type !== 'HorizontalLine') {
      const rect = (renderer as BaseRenderer).createRect(
        0,
        0,
        component.width,
        component.height,
        fullConfig
      );
      // Ensure fill is transparent
      if (rect.type === 'rect') {
        rect.fill = 'transparent';
      }
      componentElements.push(rect);
    }

    // Add wireframe content
    componentElements.push(...contentElements);

    // Wrap in group and apply position offset
    const group: WireframeElement = {
      type: 'group',
      x: component.x + offsetX,
      y: component.y + offsetY,
      elements: componentElements,
    };

    return [group];
  }

  /**
   * Update configuration
   */
  updateConfig(config: Partial<WireframeConfig>): void {
    this.config = { ...this.config, ...config };
  }

  /**
   * Get current configuration
   */
  getConfig(): WireframeConfig {
    return { ...this.config };
  }
}

