import { PlacedComponent, ComponentType } from '@/types/types';

/**
 * Base wireframe element types
 */
export type WireframeElementType = 'rect' | 'line' | 'text' | 'circle' | 'path' | 'group';

/**
 * Base interface for all wireframe elements
 */
export interface BaseWireframeElement {
  type: WireframeElementType;
  x?: number;
  y?: number;
  opacity?: number;
}

/**
 * Rectangle wireframe element
 */
export interface WireframeRect extends BaseWireframeElement {
  type: 'rect';
  x: number;
  y: number;
  width: number;
  height: number;
  fill?: string;
  stroke?: string;
  strokeWidth?: number;
  opacity?: number;
}

/**
 * Line wireframe element
 */
export interface WireframeLine extends BaseWireframeElement {
  type: 'line';
  points: number[];
  stroke?: string;
  strokeWidth?: number;
  dash?: number[];
  opacity?: number;
}

/**
 * Text wireframe element
 */
export interface WireframeText extends BaseWireframeElement {
  type: 'text';
  x: number;
  y: number;
  text: string;
  fontSize?: number;
  fill?: string;
  fontFamily?: string;
  opacity?: number;
}

/**
 * Circle wireframe element
 */
export interface WireframeCircle extends BaseWireframeElement {
  type: 'circle';
  x: number;
  y: number;
  radius: number;
  fill?: string;
  stroke?: string;
  strokeWidth?: number;
  opacity?: number;
}

/**
 * Path wireframe element (for curves)
 */
export interface WireframePath extends BaseWireframeElement {
  type: 'path';
  data: string;
  stroke?: string;
  strokeWidth?: number;
  fill?: string;
  opacity?: number;
}

/**
 * Group wireframe element (container for multiple elements)
 */
export interface WireframeGroup extends BaseWireframeElement {
  type: 'group';
  x?: number;
  y?: number;
  elements: WireframeElement[];
  opacity?: number;
}

/**
 * Union type for all wireframe elements
 */
export type WireframeElement =
  | WireframeRect
  | WireframeLine
  | WireframeText
  | WireframeCircle
  | WireframePath
  | WireframeGroup;

/**
 * Configuration passed to renderers
 */
export interface RendererConfig {
  strokeColor: string;
  fillColor: string;
  strokeWidth: number;
  fontSize: number;
  fontFamily: string;
  hasBorder?: boolean;
  // Extensible for future component details
  componentDetails?: Record<string, unknown>;
}

/**
 * Wireframe generation configuration
 */
export interface WireframeConfig {
  padding: number;
  backgroundColor: string;
  defaultStroke: string;
  defaultFill: string;
  defaultStrokeWidth: number;
  defaultFontSize: number;
  defaultFontFamily: string;
  // Component-specific overrides
  componentStyles?: Partial<Record<ComponentType, Partial<RendererConfig>>>;
  // Extensible for future details
  componentDetails?: Record<string, unknown>;
}

/**
 * Export options
 */
export interface ExportOptions {
  format: 'svg' | 'png';
  quality?: number;
  pixelRatio?: number;
}

/**
 * Wireframe renderer interface
 */
export interface IWireframeRenderer {
  /**
   * Renders a component into wireframe elements
   */
  render(component: PlacedComponent, config: RendererConfig): WireframeElement[];

  /**
   * Optional: Get default configuration for this renderer
   */
  getDefaultConfig?(): Partial<RendererConfig>;

  /**
   * Optional: Validate component data before rendering
   */
  validate?(component: PlacedComponent): boolean;
}

/**
 * Generated wireframe structure
 */
export interface WireframeStructure {
  width: number;
  height: number;
  elements: WireframeElement[];
  config: WireframeConfig;
}

