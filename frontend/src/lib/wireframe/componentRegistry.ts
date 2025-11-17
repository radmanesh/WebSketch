import { ComponentType, IWireframeRenderer, PlacedComponent } from './types';
import { TextRenderer } from './renderers/TextRenderer';
import { HeadingRenderer } from './renderers/HeadingRenderer';
import { ImageRenderer } from './renderers/ImageRenderer';
import { ButtonRenderer } from './renderers/ButtonRenderer';
import { InputRenderer } from './renderers/InputRenderer';
import { ListRenderer } from './renderers/ListRenderer';
import { TableRenderer } from './renderers/TableRenderer';
import { ContainerRenderer } from './renderers/ContainerRenderer';
import { FooterRenderer } from './renderers/FooterRenderer';
import { NavigationRenderer } from './renderers/NavigationRenderer';
import { HorizontalLineRenderer } from './renderers/HorizontalLineRenderer';

/**
 * Registry mapping component types to their renderers
 */
class ComponentRegistry {
  private renderers: Map<ComponentType, IWireframeRenderer> = new Map();

  constructor() {
    // Register all default renderers
    this.register('Text', new TextRenderer());
    this.register('Heading', new HeadingRenderer());
    this.register('ImagePlaceholder', new ImageRenderer());
    this.register('Button', new ButtonRenderer());
    this.register('Input', new InputRenderer());
    this.register('List', new ListRenderer());
    this.register('Table', new TableRenderer());
    this.register('Container', new ContainerRenderer());
    this.register('Footer', new FooterRenderer());
    this.register('NavigationBox', new NavigationRenderer());
    this.register('HorizontalLine', new HorizontalLineRenderer());
  }

  /**
   * Register a renderer for a component type
   */
  register(type: ComponentType, renderer: IWireframeRenderer): void {
    this.renderers.set(type, renderer);
  }

  /**
   * Get renderer for a component type
   */
  getRenderer(type: ComponentType): IWireframeRenderer | undefined {
    return this.renderers.get(type);
  }

  /**
   * Check if a renderer exists for a component type
   */
  hasRenderer(type: ComponentType): boolean {
    return this.renderers.has(type);
  }

  /**
   * Get all registered component types
   */
  getRegisteredTypes(): ComponentType[] {
    return Array.from(this.renderers.keys());
  }
}

// Export singleton instance
export const componentRegistry = new ComponentRegistry();

