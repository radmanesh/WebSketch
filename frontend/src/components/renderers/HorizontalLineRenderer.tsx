import { Line } from 'react-konva';
import { BaseCanvasRenderer, type CanvasRendererProps } from './BaseRenderer';

/**
 * Renders HorizontalLine component as a single horizontal line
 */
export class HorizontalLineRenderer extends BaseCanvasRenderer {
  render({ width, height, strokeColor }: CanvasRendererProps) {
    const effectiveHeight = this.getEffectiveHeight(height, 'HorizontalLine');
    const centerY = effectiveHeight / 2;
    return (
      <Line
        points={[0, centerY, width, centerY]}
        stroke={strokeColor}
        strokeWidth={2}
        listening={false}
      />
    );
  }
}
