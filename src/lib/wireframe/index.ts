/**
 * Modular Wireframe Export System
 *
 * Main entry point for wireframe generation and export
 */

// Core classes
export { WireframeGenerator } from './WireframeGenerator';
export { componentRegistry } from './componentRegistry';

// Exporters
export { SVGExporter } from './exporters/SVGExporter';
export { PNGExporter } from './exporters/PNGExporter';
export type { IWireframeExporter, BaseExporter } from './exporters/BaseExporter';

// Types
export type {
  WireframeElement,
  WireframeElementType,
  WireframeStructure,
  WireframeConfig,
  RendererConfig,
  ExportOptions,
  IWireframeRenderer,
  WireframeRect,
  WireframeLine,
  WireframeText,
  WireframeCircle,
  WireframePath,
  WireframeGroup,
} from './types';

// Configuration
export { defaultWireframeConfig, getRendererConfig, hasBorder, COMPONENTS_WITH_BORDERS } from './config';

// Renderers (for extensibility)
export { BaseRenderer } from './renderers/BaseRenderer';
export { TextRenderer } from './renderers/TextRenderer';
export { HeadingRenderer } from './renderers/HeadingRenderer';
export { ImageRenderer } from './renderers/ImageRenderer';
export { ButtonRenderer } from './renderers/ButtonRenderer';
export { InputRenderer } from './renderers/InputRenderer';
export { ListRenderer } from './renderers/ListRenderer';
export { TableRenderer } from './renderers/TableRenderer';
export { ContainerRenderer } from './renderers/ContainerRenderer';
export { FooterRenderer } from './renderers/FooterRenderer';
export { NavigationRenderer } from './renderers/NavigationRenderer';
export { HorizontalLineRenderer } from './renderers/HorizontalLineRenderer';

