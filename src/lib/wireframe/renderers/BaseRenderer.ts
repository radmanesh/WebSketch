import { IWireframeRenderer, PlacedComponent, RendererConfig, WireframeElement } from '../types';

/**
 * Base renderer class that all component renderers should extend
 * Provides common utilities and implements the interface
 */
export abstract class BaseRenderer implements IWireframeRenderer {
  /**
   * Abstract method that must be implemented by each renderer
   */
  abstract render(component: PlacedComponent, config: RendererConfig): WireframeElement[];

  /**
   * Optional default configuration
   */
  getDefaultConfig?(): Partial<RendererConfig> {
    return undefined;
  }

  /**
   * Optional validation
   */
  validate?(component: PlacedComponent): boolean {
    return component.width > 0 && component.height > 0;
  }

  /**
   * Helper to create a group element
   */
  protected createGroup(
    elements: WireframeElement[],
    x?: number,
    y?: number,
    opacity?: number
  ): WireframeElement {
    return {
      type: 'group',
      x,
      y,
      elements,
      opacity,
    };
  }

  /**
   * Helper to create a rectangle element
   */
  protected createRect(
    x: number,
    y: number,
    width: number,
    height: number,
    config: RendererConfig,
    overrides?: Partial<RendererConfig>
  ): WireframeElement {
    // For wireframe export, always use transparent fill
    const fill = overrides?.fillColor || config.fillColor || 'transparent';

    return {
      type: 'rect',
      x,
      y,
      width,
      height,
      fill: fill === 'none' ? 'transparent' : fill,
      stroke: overrides?.strokeColor || config.strokeColor,
      strokeWidth: overrides?.strokeWidth || config.strokeWidth,
    };
  }

  /**
   * Helper to create a line element
   */
  protected createLine(
    points: number[],
    config: RendererConfig,
    strokeWidth?: number,
    strokeColor?: string
  ): WireframeElement {
    return {
      type: 'line',
      points,
      stroke: strokeColor || config.strokeColor,
      strokeWidth: strokeWidth || config.strokeWidth,
    };
  }

  /**
   * Helper to create text element
   */
  protected createText(
    x: number,
    y: number,
    text: string,
    config: RendererConfig,
    fontSize?: number,
    fill?: string
  ): WireframeElement {
    return {
      type: 'text',
      x,
      y,
      text,
      fontSize: fontSize || config.fontSize,
      fill: fill || config.strokeColor,
      fontFamily: config.fontFamily,
    };
  }

  /**
   * Helper to create circle element
   */
  protected createCircle(
    x: number,
    y: number,
    radius: number,
    config: RendererConfig,
    fill?: string,
    stroke?: string
  ): WireframeElement {
    return {
      type: 'circle',
      x,
      y,
      radius,
      fill: fill || 'transparent',
      stroke: stroke || config.strokeColor,
      strokeWidth: config.strokeWidth,
    };
  }
}

