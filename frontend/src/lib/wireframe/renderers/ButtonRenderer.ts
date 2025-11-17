import { BaseRenderer } from './BaseRenderer';
import { PlacedComponent, RendererConfig, WireframeElement } from '../types';

/**
 * Renders Button component with "btn" label
 */
export class ButtonRenderer extends BaseRenderer {
  render(component: PlacedComponent, config: RendererConfig): WireframeElement[] {
    const elements: WireframeElement[] = [];

    // Button label
    elements.push(
      this.createText(8, 8, 'btn', config)
    );

    return elements;
  }
}

