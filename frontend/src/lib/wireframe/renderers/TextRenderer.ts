import { BaseRenderer } from './BaseRenderer';
import { PlacedComponent, RendererConfig, WireframeElement } from '../types';

/**
 * Renders Text component with wavy horizontal lines
 */
export class TextRenderer extends BaseRenderer {
  render(component: PlacedComponent, config: RendererConfig): WireframeElement[] {
    const { width, height } = component;
    const elements: WireframeElement[] = [];

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

      elements.push(
        this.createLine(points, config, 1.5, config.strokeColor)
      );

      currentY += lineSpacing;
    }

    return elements;
  }
}

