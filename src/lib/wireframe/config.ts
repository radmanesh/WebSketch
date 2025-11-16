import { WireframeConfig, ComponentType } from './types';

/**
 * Components that should have borders in export
 */
export const COMPONENTS_WITH_BORDERS: ComponentType[] = [
  'Container',
  'Button',
  'Input',
  'ImagePlaceholder',
  'NavigationBox',
];

/**
 * Default wireframe configuration
 */
export const defaultWireframeConfig: WireframeConfig = {
  padding: 20,
  backgroundColor: '#ffffff',
  defaultStroke: '#333333',
  defaultFill: 'transparent', // No fill in exports
  defaultStrokeWidth: 2,
  defaultFontSize: 14,
  defaultFontFamily: 'Arial, sans-serif',
  componentStyles: {
    // Components with borders - gray stroke, no fill
    Container: {
      strokeColor: '#333333',
      fillColor: 'transparent',
    },
    Button: {
      strokeColor: '#333333',
      fillColor: 'transparent',
    },
    Input: {
      strokeColor: '#333333',
      fillColor: 'transparent',
    },
    ImagePlaceholder: {
      strokeColor: '#333333',
      fillColor: 'transparent',
    },
    NavigationBox: {
      strokeColor: '#333333',
      fillColor: 'transparent',
    },
    // Components without borders - no stroke on container
    Text: {
      strokeColor: '#808080', // Gray for wavy lines
      fillColor: 'transparent',
      strokeWidth: 0, // No border
    },
    Heading: {
      strokeColor: '#000000', // Black for bold lines
      fillColor: 'transparent',
      strokeWidth: 0, // No border
    },
    List: {
      strokeColor: '#000000', // Black for wavy lines
      fillColor: 'transparent',
      strokeWidth: 0, // No border
    },
    Footer: {
      strokeColor: '#666666',
      fillColor: 'transparent',
      strokeWidth: 0, // No border
    },
    Table: {
      strokeColor: '#666666',
      fillColor: 'transparent',
      strokeWidth: 0, // No border
    },
    HorizontalLine: {
      strokeColor: '#666666',
      fillColor: 'transparent',
      strokeWidth: 0, // No border
    },
  },
};

/**
 * Check if a component type should have a border
 */
export function hasBorder(type: ComponentType): boolean {
  return COMPONENTS_WITH_BORDERS.includes(type);
}

/**
 * Get renderer configuration for a specific component type
 */
export function getRendererConfig(
  type: ComponentType,
  globalConfig: WireframeConfig
): {
  strokeColor: string;
  fillColor: string;
  strokeWidth: number;
  fontSize: number;
  fontFamily: string;
  hasBorder: boolean;
} {
  const componentStyle = globalConfig.componentStyles?.[type] || {};

  return {
    strokeColor: componentStyle.strokeColor || globalConfig.defaultStroke,
    fillColor: componentStyle.fillColor || globalConfig.defaultFill,
    strokeWidth: componentStyle.strokeWidth || globalConfig.defaultStrokeWidth,
    fontSize: componentStyle.fontSize || globalConfig.defaultFontSize,
    fontFamily: componentStyle.fontFamily || globalConfig.defaultFontFamily,
    hasBorder: hasBorder(type),
  };
}

