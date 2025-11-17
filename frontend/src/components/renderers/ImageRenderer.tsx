import { Line } from 'react-konva';
import { BaseCanvasRenderer, type CanvasRendererProps } from './BaseRenderer';

/**
 * Renders ImagePlaceholder component with X mark
 */
export class ImageRenderer extends BaseCanvasRenderer {
  render({ width, height, strokeColor }: CanvasRendererProps) {
    const centerX = width / 2;
    const centerY = height / 2;
    const xSize = Math.min(width, height) * 0.3;

    return (
      <>
        <Line
          points={[centerX - xSize, centerY - xSize, centerX + xSize, centerY + xSize]}
          stroke={strokeColor}
          strokeWidth={3}
          listening={false}
        />
        <Line
          points={[centerX - xSize, centerY + xSize, centerX + xSize, centerY - xSize]}
          stroke={strokeColor}
          strokeWidth={3}
          listening={false}
        />
      </>
    );
  }
}
