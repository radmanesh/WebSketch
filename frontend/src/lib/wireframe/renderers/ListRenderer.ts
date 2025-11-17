import { BaseRenderer } from './BaseRenderer';
import { PlacedComponent } from '@/types/types';
import { RendererConfig, WireframeElement } from '../types';

/**
 * Renders List component with repeated wavy horizontal lines and circles
 */
export class ListRenderer extends BaseRenderer {
  render(component: PlacedComponent, config: RendererConfig): WireframeElement[] {
    const { width, height } = component;
    const elements: WireframeElement[] = [];

    const lineSpacing = 25;
    const circleRadius = 4;
    const circleX = 15;
    const waveAmplitude = 2;
    const waveLength = 20;
    let currentY = 15;

    while (currentY < height - 10) {
      // Circle
      elements.push(
        this.createCircle(circleX, currentY, circleRadius, config, 'transparent', config.strokeColor)
      );

      // Wavy line instead of straight
      const lineStartX = circleX + circleRadius + 8;
      const points: number[] = [];
      for (let xPos = lineStartX; xPos < width - 10; xPos += 2) {
        const waveY = Math.sin((xPos / waveLength) * Math.PI * 2) * waveAmplitude;
        points.push(xPos, currentY + waveY);
      }

      if (points.length > 0) {
        elements.push(
          this.createLine(
            points,
            config,
            config.strokeWidth || 2,
            config.strokeColor
          )
        );
      }

      currentY += lineSpacing;
    }

    return elements;
  }
}

