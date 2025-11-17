import { BaseRenderer } from './BaseRenderer';
import { PlacedComponent } from '@/types/types';
import { RendererConfig, WireframeElement } from '../types';

/**
 * Renders Table component with grid pattern
 */
export class TableRenderer extends BaseRenderer {
  render(component: PlacedComponent, config: RendererConfig): WireframeElement[] {
    const { width, height } = component;
    const elements: WireframeElement[] = [];

    const rowCount = Math.max(2, Math.floor(height / 30));
    const colCount = Math.max(2, Math.floor(width / 80));
    const rowHeight = height / rowCount;
    const colWidth = width / colCount;

    // Horizontal lines
    for (let i = 0; i <= rowCount; i++) {
      elements.push(
        this.createLine(
          [0, i * rowHeight, width, i * rowHeight],
          config,
          1.5,
          config.strokeColor
        )
      );
    }

    // Vertical lines
    for (let i = 0; i <= colCount; i++) {
      elements.push(
        this.createLine(
          [i * colWidth, 0, i * colWidth, height],
          config,
          1.5,
          config.strokeColor
        )
      );
    }

    return elements;
  }
}

