import { BaseRenderer } from './BaseRenderer';
import { PlacedComponent, RendererConfig, WireframeElement } from '../types';

/**
 * Renders ImagePlaceholder component with X mark
 */
export class ImageRenderer extends BaseRenderer {
  render(component: PlacedComponent, config: RendererConfig): WireframeElement[] {
    const { width, height } = component;
    const elements: WireframeElement[] = [];

    const centerX = width / 2;
    const centerY = height / 2;
    const xSize = Math.min(width, height) * 0.3;

    // X mark - two diagonal lines
    elements.push(
      this.createLine(
        [centerX - xSize, centerY - xSize, centerX + xSize, centerY + xSize],
        config,
        3,
        config.strokeColor
      ),
      this.createLine(
        [centerX - xSize, centerY + xSize, centerX + xSize, centerY - xSize],
        config,
        3,
        config.strokeColor
      )
    );

    return elements;
  }
}

