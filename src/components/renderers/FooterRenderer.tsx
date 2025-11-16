import { BaseCanvasRenderer, type CanvasRendererProps } from './BaseRenderer';

/**
 * Renders Footer component (no special content, just border)
 */
export class FooterRenderer extends BaseCanvasRenderer {
  render(): JSX.Element | null {
    return null; // Footer has no content, just border
  }
}
