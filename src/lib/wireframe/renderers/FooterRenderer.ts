import { BaseRenderer } from './BaseRenderer';
import { PlacedComponent, RendererConfig, WireframeElement } from '../types';

/**
 * Renders Footer component - simple box, no special content
 */
export class FooterRenderer extends BaseRenderer {
  render(component: PlacedComponent, config: RendererConfig): WireframeElement[] {
    // Footer is just a box, no additional wireframe content
    return [];
  }
}

