import { BaseRenderer } from './BaseRenderer';
import { PlacedComponent, RendererConfig, WireframeElement } from '../types';

/**
 * Renders HorizontalLine component as a single horizontal line
 */
export class HorizontalLineRenderer extends BaseRenderer {
  render(component: PlacedComponent, config: RendererConfig): WireframeElement[] {
    const { width, height } = component;
    const centerY = Math.max(height, 2) / 2;

    return [
      this.createLine(
        [0, centerY, width, centerY],
        config,
        config.strokeWidth,
        config.strokeColor
      )
    ];
  }
}

