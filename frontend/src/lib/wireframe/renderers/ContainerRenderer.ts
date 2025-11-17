import { BaseRenderer } from './BaseRenderer';
import { PlacedComponent } from '@/types/types';
import { RendererConfig, WireframeElement } from '../types';

/**
 * Renders Container component - simple box, no special content
 */
export class ContainerRenderer extends BaseRenderer {
  render(component: PlacedComponent, config: RendererConfig): WireframeElement[] {
    // Container is just a box, no additional wireframe content
    return [];
  }
}

