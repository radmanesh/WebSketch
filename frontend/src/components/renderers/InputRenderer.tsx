import type { ReactNode } from 'react';
import { BaseCanvasRenderer, type CanvasRendererProps } from './BaseRenderer';

/**
 * Renders Input component (label is handled separately in PlacedComponentShape)
 */
export class InputRenderer extends BaseCanvasRenderer {
  render(): ReactNode {
    return null; // Input label is handled separately, no wireframe content
  }
}
