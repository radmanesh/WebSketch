import { Line } from 'react-konva';
import { BaseCanvasRenderer, type CanvasRendererProps } from './BaseRenderer';

/**
 * Renders Text component with wavy horizontal lines
 */
export class TextRenderer extends BaseCanvasRenderer {
  render({ width, height, strokeColor }: CanvasRendererProps) {
    const lines: JSX.Element[] = [];
    const lineSpacing = 20;
    const waveAmplitude = 3;
    const waveLength = 30;
    let currentY = 15;

    while (currentY < height - 10) {
      const points: number[] = [];
      for (let xPos = 10; xPos < width - 10; xPos += 2) {
        const waveY = Math.sin((xPos / waveLength) * Math.PI * 2) * waveAmplitude;
        points.push(xPos, currentY + waveY);
      }
      lines.push(
        <Line
          key={currentY}
          points={points}
          stroke={strokeColor}
          strokeWidth={1.5}
          tension={0.5}
          listening={false}
        />
      );
      currentY += lineSpacing;
    }
    return lines;
  }
}
