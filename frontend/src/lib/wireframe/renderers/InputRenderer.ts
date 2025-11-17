import { BaseRenderer } from './BaseRenderer';
import { PlacedComponent, RendererConfig, WireframeElement } from '../types';

/**
 * Renders Input component with "input" label
 */
export class InputRenderer extends BaseRenderer {
  render(component: PlacedComponent, config: RendererConfig): WireframeElement[] {
    const elements: WireframeElement[] = [];

    // Input label
    elements.push(
      this.createText(8, 8, 'input', config)
    );

    return elements;
  }
}

