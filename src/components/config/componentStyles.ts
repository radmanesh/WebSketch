import { ComponentType } from '@/types/types';

/**
 * Components that should have borders in canvas display
 */
export const COMPONENTS_WITH_BORDERS: ComponentType[] = [
  'Container',
  'Button',
  'Input',
  'ImagePlaceholder',
  'NavigationBox',
];

/**
 * Check if a component type should have a border
 */
export const getComponentHasBorder = (type: ComponentType): boolean => {
  return COMPONENTS_WITH_BORDERS.includes(type);
};

/**
 * Get background color for component display (transparent overlay for visibility)
 */
export const getComponentColor = (type: ComponentType): string => {
  // Very transparent background for all components (display only, not exported)
  return 'rgba(128, 128, 128, 0.1)'; // Light gray with 10% opacity
};

/**
 * Get stroke color for component based on type
 */
export const getComponentStroke = (type: ComponentType): string => {
  switch (type) {
    // Components with borders - gray stroke
    case 'Container':
    case 'Button':
    case 'Input':
    case 'ImagePlaceholder':
    case 'NavigationBox':
      return '#333333'; // Dark gray for borders
    // Components without borders - grayscale for content
    case 'Text':
      return '#808080'; // Gray for wavy lines
    case 'Heading':
      return '#000000'; // Black for bold lines
    case 'List':
      return '#000000'; // Black for wavy lines
    case 'Footer':
    case 'Table':
      return '#666666'; // Medium gray
    case 'HorizontalLine':
      return '#666666'; // Medium gray
    default:
      return '#808080';
  }
};

/**
 * Get content stroke color for wireframe rendering
 * (For non-border components, this is the color used for the content lines/shapes)
 */
export const getContentStrokeColor = (type: ComponentType): string => {
  if (type === 'Text') {
    return '#808080'; // Gray for wavy lines
  } else if (type === 'Heading' || type === 'List') {
    return '#000000'; // Black for bold/wavy lines
  } else if (type === 'Footer' || type === 'Table' || type === 'HorizontalLine') {
    return '#666666'; // Medium gray
  }
  return getComponentStroke(type);
};
