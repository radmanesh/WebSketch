import { ComponentType } from '@/types/types';
import type { ICanvasRenderer } from '../renderers/BaseRenderer';
import { componentRegistry } from './componentRegistry';
import {
  getComponentHasBorder,
  getComponentColor,
  getComponentStroke,
  getContentStrokeColor,
  COMPONENTS_WITH_BORDERS,
} from '../config/componentStyles';

/**
 * Component configuration interface
 */
export interface ComponentConfig {
  hasBorder?: boolean;
  strokeColor?: string;
  fillColor?: string;
  contentStrokeColor?: string;
}

/**
 * Centralized Component Manager
 * Provides interface for managing component registration, rendering, and configuration
 * Designed to be extensible by LLMs
 */
class ComponentManager {
  private configs: Map<ComponentType, ComponentConfig> = new Map();

  constructor() {
    // Initialize default configurations
    this.initializeDefaultConfigs();
  }

  /**
   * Initialize default configurations for all component types
   */
  private initializeDefaultConfigs(): void {
    const allTypes: ComponentType[] = [
      'Container',
      'Button',
      'Input',
      'ImagePlaceholder',
      'Text',
      'HorizontalLine',
      'Heading',
      'Footer',
      'NavigationBox',
      'List',
      'Table',
    ];

    allTypes.forEach((type) => {
      this.configs.set(type, {
        hasBorder: getComponentHasBorder(type),
        strokeColor: getComponentStroke(type),
        fillColor: getComponentColor(type),
        contentStrokeColor: getContentStrokeColor(type),
      });
    });
  }

  /**
   * Register a new component renderer
   * Allows dynamic addition of new component types
   */
  registerRenderer(type: ComponentType, renderer: ICanvasRenderer): void {
    componentRegistry.register(type, renderer);

    // Initialize default config if not exists
    if (!this.configs.has(type)) {
      this.configs.set(type, {
        hasBorder: getComponentHasBorder(type),
        strokeColor: getComponentStroke(type),
        fillColor: getComponentColor(type),
        contentStrokeColor: getContentStrokeColor(type),
      });
    }
  }

  /**
   * Get renderer for a component type
   */
  getRenderer(type: ComponentType): ICanvasRenderer | undefined {
    return componentRegistry.getRenderer(type);
  }

  /**
   * Get component configuration
   */
  getComponentConfig(type: ComponentType): ComponentConfig | undefined {
    return this.configs.get(type);
  }

  /**
   * Update component configuration
   * Allows LLMs to modify component styles/behavior
   */
  updateComponentConfig(type: ComponentType, config: Partial<ComponentConfig>): void {
    const currentConfig = this.configs.get(type) || {};
    this.configs.set(type, { ...currentConfig, ...config });
  }

  /**
   * Get all registered component types
   */
  getAllComponentTypes(): ComponentType[] {
    return componentRegistry.getRegisteredTypes();
  }

  /**
   * Check if component has border
   */
  hasBorder(type: ComponentType): boolean {
    const config = this.getComponentConfig(type);
    return config?.hasBorder ?? getComponentHasBorder(type);
  }

  /**
   * Get stroke color for component
   */
  getStrokeColor(type: ComponentType): string {
    const config = this.getComponentConfig(type);
    return config?.strokeColor ?? getComponentStroke(type);
  }

  /**
   * Get fill color for component
   */
  getFillColor(type: ComponentType): string {
    const config = this.getComponentConfig(type);
    return config?.fillColor ?? getComponentColor(type);
  }

  /**
   * Get content stroke color for component
   */
  getContentStrokeColor(type: ComponentType): string {
    const config = this.getComponentConfig(type);
    return config?.contentStrokeColor ?? getContentStrokeColor(type);
  }

  /**
   * Get list of components with borders
   */
  getComponentsWithBorders(): ComponentType[] {
    return COMPONENTS_WITH_BORDERS;
  }

  /**
   * Reset all configurations to defaults
   */
  resetConfigurations(): void {
    this.configs.clear();
    this.initializeDefaultConfigs();
  }
}

// Export singleton instance for easy access
export const componentManager = new ComponentManager();
