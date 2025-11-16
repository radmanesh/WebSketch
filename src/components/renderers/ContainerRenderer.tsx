import { BaseCanvasRenderer, type CanvasRendererProps } from './BaseRenderer';

/**
 * Renders Container component (no special content, just border)
 */
export class ContainerRenderer extends BaseCanvasRenderer {
  render(): JSX.Element | null {
    return null; // Container has no content, just border
  }
}
