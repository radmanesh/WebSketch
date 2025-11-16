import { BaseCanvasRenderer, type CanvasRendererProps } from './BaseRenderer';

/**
 * Renders Button component (label is handled separately in PlacedComponentShape)
 */
export class ButtonRenderer extends BaseCanvasRenderer {
  render(): JSX.Element | null {
    return null; // Button label is handled separately, no wireframe content
  }
}
