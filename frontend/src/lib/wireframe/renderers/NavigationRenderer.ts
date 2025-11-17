import { BaseRenderer } from './BaseRenderer';
import { PlacedComponent } from '@/types/types';
import { RendererConfig, WireframeElement } from '../types';

/**
 * Renders NavigationBox component with hamburger icon
 */
export class NavigationRenderer extends BaseRenderer {
  render(component: PlacedComponent, config: RendererConfig): WireframeElement[] {
    const { width, height } = component;
    const elements: WireframeElement[] = [];

    const iconSize = Math.min(20, width - 20, height - 20);
    const iconX = 10;
    const iconY = 10;
    const lineSpacing = iconSize / 4;
    const lineWidth = iconSize * 0.6;

    // Three horizontal lines for hamburger icon
    for (let i = 0; i < 3; i++) {
      elements.push(
        this.createLine(
          [iconX, iconY + i * lineSpacing, iconX + lineWidth, iconY + i * lineSpacing],
          config,
          config.strokeWidth,
          config.strokeColor
        )
      );
    }

    return elements;
  }
}

