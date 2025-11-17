import { PlacedComponent } from '@/types/types';
import type { ReactNode } from 'react';

/**
 * Props passed to all canvas renderers
 */
export interface CanvasRendererProps {
  component: PlacedComponent;
  isSelected: boolean;
  width: number;
  height: number;
  strokeColor: string;
}

/**
 * Base interface for canvas renderers
 * Each renderer should implement this to render a specific component type
 */
export interface ICanvasRenderer {
  /**
   * Render the wireframe content for a component
   * Returns React Konva JSX elements
   */
  render(props: CanvasRendererProps): ReactNode;
}

/**
 * Base renderer class with common utilities
 */
export abstract class BaseCanvasRenderer implements ICanvasRenderer {
  abstract render(props: CanvasRendererProps): ReactNode;

  /**
   * Calculate effective height (for components like HorizontalLine with minimum height)
   */
  protected getEffectiveHeight(height: number, type: string): number {
    if (type === 'HorizontalLine') {
      return Math.max(height, 2);
    }
    return height;
  }
}
