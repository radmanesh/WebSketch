import { Line, Circle } from 'react-konva';
import { BaseCanvasRenderer, type CanvasRendererProps } from './BaseRenderer';

/**
 * Renders List component with wavy horizontal lines and circles
 */
export class ListRenderer extends BaseCanvasRenderer {
  render({ width, height, strokeColor }: CanvasRendererProps) {
    const elements: JSX.Element[] = [];
    const lineSpacing = 25;
    const circleRadius = 4;
    const circleX = 15;
    const waveAmplitude = 2;
    const waveLength = 20;
    let currentY = 15;

    while (currentY < height - 10) {
      // Circle
      elements.push(
        <Circle
          key={`circle-${currentY}`}
          x={circleX}
          y={currentY}
          radius={circleRadius}
          stroke={strokeColor}
          strokeWidth={2}
          fill="transparent"
          listening={false}
        />
      );
      // Wavy line
      const lineStartX = circleX + circleRadius + 8;
      const points: number[] = [];
      for (let xPos = lineStartX; xPos < width - 10; xPos += 2) {
        const waveY = Math.sin((xPos / waveLength) * Math.PI * 2) * waveAmplitude;
        points.push(xPos, currentY + waveY);
      }
      if (points.length > 0) {
        elements.push(
          <Line
            key={`line-${currentY}`}
            points={points}
            stroke={strokeColor}
            strokeWidth={2}
            tension={0.5}
            listening={false}
          />
        );
      }
      currentY += lineSpacing;
    }
    return elements;
  }
}
