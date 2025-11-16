/**
 * Public exports for components
 */

// Main UI components
export { default as CanvasContainer } from './canvas/CanvasContainer';
export { default as PlacedComponentShape } from './canvas/PlacedComponentShape';
export { default as DraftBox } from './canvas/DraftBox';
export { default as PaletteSidebar } from './sidebar/PaletteSidebar';
export { default as Toolbar } from './toolbar/Toolbar';
export { default as ChatPanel } from './chat/ChatPanel';

// Component Manager and Registry (for extensibility)
export { componentManager } from './manager/ComponentManager';
export { componentRegistry } from './manager/componentRegistry';
export type { ComponentConfig } from './manager/ComponentManager';

// Renderers (for extensibility)
export * from './renderers/BaseRenderer';
export { TextRenderer } from './renderers/TextRenderer';
export { HeadingRenderer } from './renderers/HeadingRenderer';
export { ImageRenderer } from './renderers/ImageRenderer';
export { ListRenderer } from './renderers/ListRenderer';
export { TableRenderer } from './renderers/TableRenderer';
export { NavigationRenderer } from './renderers/NavigationRenderer';
export { HorizontalLineRenderer } from './renderers/HorizontalLineRenderer';
export { ContainerRenderer } from './renderers/ContainerRenderer';
export { FooterRenderer } from './renderers/FooterRenderer';
export { ButtonRenderer } from './renderers/ButtonRenderer';
export { InputRenderer } from './renderers/InputRenderer';

// Configuration (for extensibility)
export * from './config/componentStyles';
