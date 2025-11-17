import type { ReactNode } from 'react';
import { BaseCanvasRenderer, type CanvasRendererProps } from './BaseRenderer';

/**
 * Renders Footer component (no special content, just border)
 */
export class FooterRenderer extends BaseCanvasRenderer {
  render(): ReactNode {
    return null; // Footer has no content, just border
  }
}
