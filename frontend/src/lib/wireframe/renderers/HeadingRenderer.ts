import { BaseRenderer } from './BaseRenderer';
import { PlacedComponent } from '@/types/types';
import { RendererConfig, WireframeElement } from '../types';

/**
 * Renders Heading component with bold straight horizontal lines
 */
export class HeadingRenderer extends BaseRenderer {
  render(component: PlacedComponent, config: RendererConfig): WireframeElement[] {
    const { width, height } = component;
    const elements: WireframeElement[] = [];

    const lineSpacing = 25;
    const lineThickness = 4;
    let currentY = 15;

    while (currentY < height - 10) {
      elements.push(
        this.createLine(
          [10, currentY, width - 10, currentY],
          config,
          lineThickness,
          '#000000'
        )
      );
      currentY += lineSpacing;
    }

    return elements;
  }
}

