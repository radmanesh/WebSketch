export type ComponentType = 'Container' | 'Button' | 'Input' | 'ImagePlaceholder';

export interface PlacedComponent {
  id: string;
  type: ComponentType;
  x: number;
  y: number;
  width: number;
  height: number;
  props: Record<string, unknown>;
}

export type Mode = 'draw' | 'select';
