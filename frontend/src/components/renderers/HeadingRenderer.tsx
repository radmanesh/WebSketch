import { Line } from 'react-konva';
import { BaseCanvasRenderer, type CanvasRendererProps } from './BaseRenderer';

/**
 * Renders Heading component with bold straight lines
 */
export class HeadingRenderer extends BaseCanvasRenderer {
  render({ width, height }: CanvasRendererProps) {
    const lines: JSX.Element[] = [];
    const lineSpacing = 25;
    const lineThickness = 4;
    let currentY = 15;

    while (currentY < height - 10) {
      lines.push(
        <Line
          key={currentY}
          points={[10, currentY, width - 10, currentY]}
          stroke="#000000"
          strokeWidth={lineThickness}
          listening={false}
        />
      );
      currentY += lineSpacing;
    }
    return lines;
  }
}
