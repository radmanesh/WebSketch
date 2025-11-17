import type { ReactNode } from 'react';
import { BaseCanvasRenderer, type CanvasRendererProps } from './BaseRenderer';

/**
 * Renders Container component (no special content, just border)
 */
export class ContainerRenderer extends BaseCanvasRenderer {
  render(): ReactNode {
    return null; // Container has no content, just border
  }
}
