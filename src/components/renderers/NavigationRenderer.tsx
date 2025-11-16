import { Line } from 'react-konva';
import { BaseCanvasRenderer, type CanvasRendererProps } from './BaseRenderer';

/**
 * Renders NavigationBox component with hamburger icon (3 horizontal lines)
 */
export class NavigationRenderer extends BaseCanvasRenderer {
  render({ width, height, strokeColor }: CanvasRendererProps) {
    const lines: JSX.Element[] = [];
    const iconSize = Math.min(20, width - 20, height - 20);
    const iconX = 10;
    const iconY = 10;
    const lineSpacing = iconSize / 4;
    const lineWidth = iconSize * 0.6;

    // Three horizontal lines for hamburger
    for (let i = 0; i < 3; i++) {
      lines.push(
        <Line
          key={`hamburger-${i}`}
          points={[iconX, iconY + i * lineSpacing, iconX + lineWidth, iconY + i * lineSpacing]}
          stroke={strokeColor}
          strokeWidth={2}
          listening={false}
        />
      );
    }
    return lines;
  }
}
