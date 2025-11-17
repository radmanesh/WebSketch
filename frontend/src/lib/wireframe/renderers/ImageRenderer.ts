import { BaseRenderer } from './BaseRenderer';
import { PlacedComponent, RendererConfig, WireframeElement } from '../types';

/**
 * Renders ImagePlaceholder component with X mark
 */
export class ImageRenderer extends BaseRenderer {
  render(component: PlacedComponent, config: RendererConfig): WireframeElement[] {
    const { width, height } = component;
    const elements: WireframeElement[] = [];

    // X mark - two full corner-to-corner diagonal lines
    elements.push(
      // Diagonal from top-left to bottom-right
      this.createLine(
        [0, 0, width, height],
        config,
        3,
        config.strokeColor
      ),
      // Diagonal from top-right to bottom-left
      this.createLine(
        [width, 0, 0, height],
        config,
        3,
        config.strokeColor
      )
    );

    return elements;
  }
}

