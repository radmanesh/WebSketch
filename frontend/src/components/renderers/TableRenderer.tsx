import type { ReactNode } from 'react';
import { Line } from 'react-konva';
import { BaseCanvasRenderer, type CanvasRendererProps } from './BaseRenderer';

/**
 * Renders Table component with grid pattern
 */
export class TableRenderer extends BaseCanvasRenderer {
  render({ width, height, strokeColor }: CanvasRendererProps): ReactNode {
    const lines: ReactNode[] = [];
    const rowCount = Math.max(2, Math.floor(height / 30));
    const colCount = Math.max(2, Math.floor(width / 80));
    const rowHeight = height / rowCount;
    const colWidth = width / colCount;

    // Horizontal lines
    for (let i = 0; i <= rowCount; i++) {
      lines.push(
        <Line
          key={`h-${i}`}
          points={[0, i * rowHeight, width, i * rowHeight]}
          stroke={strokeColor}
          strokeWidth={1.5}
          listening={false}
        />
      );
    }

    // Vertical lines
    for (let i = 0; i <= colCount; i++) {
      lines.push(
        <Line
          key={`v-${i}`}
          points={[i * colWidth, 0, i * colWidth, height]}
          stroke={strokeColor}
          strokeWidth={1.5}
          listening={false}
        />
      );
    }
    return lines;
  }
}
