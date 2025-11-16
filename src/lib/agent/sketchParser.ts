import { PlacedComponent } from '@/types/types';

export interface LayoutAnalysis {
  description: string;
  components: ComponentDescription[];
  spatialRelationships: SpatialRelationship[];
  layoutStats: LayoutStats;
}

export interface ComponentDescription {
  id: string;
  type: string;
  position: string;
  size: string;
  description: string;
}

export interface SpatialRelationship {
  component1: string;
  component2: string;
  relationship: 'above' | 'below' | 'left' | 'right' | 'overlapping' | 'aligned';
  distance?: number;
}

export interface LayoutStats {
  canvasWidth: number;
  canvasHeight: number;
  componentCount: number;
  componentTypes: Record<string, number>;
  leftColumn?: ComponentGroup;
  rightColumn?: ComponentGroup;
  topSection?: ComponentGroup;
  bottomSection?: ComponentGroup;
}

export interface ComponentGroup {
  components: string[];
  bounds: { x: number; y: number; width: number; height: number };
}

export function parseSketch(components: PlacedComponent[]): LayoutAnalysis {
  if (components.length === 0) {
    return {
      description: 'Empty sketch with no components',
      components: [],
      spatialRelationships: [],
      layoutStats: {
        canvasWidth: 0,
        canvasHeight: 0,
        componentCount: 0,
        componentTypes: {},
      },
    };
  }

  // Calculate canvas bounds
  const bounds = calculateBounds(components);

  // Generate component descriptions
  const componentDescriptions = components.map(comp => describeComponent(comp, bounds));

  // Identify spatial relationships
  const relationships = identifyRelationships(components);

  // Analyze layout structure
  const stats = analyzeLayout(components, bounds);

  // Generate overall description
  const description = generateDescription(components, stats, relationships);

  return {
    description,
    components: componentDescriptions,
    spatialRelationships: relationships,
    layoutStats: stats,
  };
}

function calculateBounds(components: PlacedComponent[]): { minX: number; minY: number; maxX: number; maxY: number } {
  let minX = Infinity;
  let minY = Infinity;
  let maxX = -Infinity;
  let maxY = -Infinity;

  components.forEach(comp => {
    minX = Math.min(minX, comp.x);
    minY = Math.min(minY, comp.y);
    maxX = Math.max(maxX, comp.x + comp.width);
    maxY = Math.max(maxY, comp.y + comp.height);
  });

  return { minX, minY, maxX, maxY };
}

function describeComponent(component: PlacedComponent, bounds: { minX: number; minY: number; maxX: number; maxY: number }): ComponentDescription {
  const canvasWidth = bounds.maxX - bounds.minX;
  const canvasHeight = bounds.maxY - bounds.minY;

  const xPercent = ((component.x - bounds.minX) / canvasWidth * 100).toFixed(1);
  const yPercent = ((component.y - bounds.minY) / canvasHeight * 100).toFixed(1);

  let position = '';
  if (component.x < canvasWidth * 0.33) {
    position = 'left side';
  } else if (component.x > canvasWidth * 0.66) {
    position = 'right side';
  } else {
    position = 'center';
  }

  if (component.y < canvasHeight * 0.33) {
    position += ', top section';
  } else if (component.y > canvasHeight * 0.66) {
    position += ', bottom section';
  } else {
    position += ', middle section';
  }

  const size = `${Math.round(component.width)}x${Math.round(component.height)}px`;

  return {
    id: component.id,
    type: component.type,
    position,
    size,
    description: `${component.type} at ${position} (${xPercent}%, ${yPercent}%), size ${size}`,
  };
}

function identifyRelationships(components: PlacedComponent[]): SpatialRelationship[] {
  const relationships: SpatialRelationship[] = [];
  const threshold = 20; // pixels

  for (let i = 0; i < components.length; i++) {
    for (let j = i + 1; j < components.length; j++) {
      const comp1 = components[i];
      const comp2 = components[j];

      // Check for overlapping
      if (isOverlapping(comp1, comp2)) {
        relationships.push({
          component1: comp1.id,
          component2: comp2.id,
          relationship: 'overlapping',
        });
        continue;
      }

      // Check vertical relationships
      const verticalDistance = Math.abs((comp1.y + comp1.height / 2) - (comp2.y + comp2.height / 2));
      const horizontalOverlap = Math.max(0, Math.min(comp1.x + comp1.width, comp2.x + comp2.width) - Math.max(comp1.x, comp2.x));

      if (horizontalOverlap > Math.min(comp1.width, comp2.width) * 0.5) {
        if (comp1.y + comp1.height < comp2.y) {
          relationships.push({
            component1: comp1.id,
            component2: comp2.id,
            relationship: 'above',
            distance: comp2.y - (comp1.y + comp1.height),
          });
        } else if (comp2.y + comp2.height < comp1.y) {
          relationships.push({
            component1: comp1.id,
            component2: comp2.id,
            relationship: 'below',
            distance: comp1.y - (comp2.y + comp2.height),
          });
        }
      }

      // Check horizontal relationships
      const horizontalDistance = Math.abs((comp1.x + comp1.width / 2) - (comp2.x + comp2.width / 2));
      const verticalOverlap = Math.max(0, Math.min(comp1.y + comp1.height, comp2.y + comp2.height) - Math.max(comp1.y, comp2.y));

      if (verticalOverlap > Math.min(comp1.height, comp2.height) * 0.5) {
        if (comp1.x + comp1.width < comp2.x) {
          relationships.push({
            component1: comp1.id,
            component2: comp2.id,
            relationship: 'left',
            distance: comp2.x - (comp1.x + comp1.width),
          });
        } else if (comp2.x + comp2.width < comp1.x) {
          relationships.push({
            component1: comp1.id,
            component2: comp2.id,
            relationship: 'right',
            distance: comp1.x - (comp2.x + comp2.width),
          });
        }
      }

      // Check alignment
      if (Math.abs(comp1.x - comp2.x) < threshold) {
        relationships.push({
          component1: comp1.id,
          component2: comp2.id,
          relationship: 'aligned',
        });
      }
    }
  }

  return relationships;
}

function isOverlapping(comp1: PlacedComponent, comp2: PlacedComponent): boolean {
  return !(
    comp1.x + comp1.width < comp2.x ||
    comp2.x + comp2.width < comp1.x ||
    comp1.y + comp1.height < comp2.y ||
    comp2.y + comp2.height < comp1.y
  );
}

function analyzeLayout(components: PlacedComponent[], bounds: { minX: number; minY: number; maxX: number; maxY: number }): LayoutStats {
  const canvasWidth = bounds.maxX - bounds.minX;
  const canvasHeight = bounds.maxY - bounds.minY;
  const componentTypes: Record<string, number> = {};

  components.forEach(comp => {
    componentTypes[comp.type] = (componentTypes[comp.type] || 0) + 1;
  });

  // Identify columns (simple heuristic: group by x position)
  const midX = bounds.minX + canvasWidth / 2;
  const leftComponents = components.filter(c => c.x + c.width / 2 < midX).map(c => c.id);
  const rightComponents = components.filter(c => c.x + c.width / 2 >= midX).map(c => c.id);

  const leftColumn = leftComponents.length > 0 ? {
    components: leftComponents,
    bounds: calculateGroupBounds(components.filter(c => leftComponents.includes(c.id))),
  } : undefined;

  const rightColumn = rightComponents.length > 0 ? {
    components: rightComponents,
    bounds: calculateGroupBounds(components.filter(c => rightComponents.includes(c.id))),
  } : undefined;

  // Identify top and bottom sections
  const midY = bounds.minY + canvasHeight / 2;
  const topComponents = components.filter(c => c.y + c.height / 2 < midY).map(c => c.id);
  const bottomComponents = components.filter(c => c.y + c.height / 2 >= midY).map(c => c.id);

  const topSection = topComponents.length > 0 ? {
    components: topComponents,
    bounds: calculateGroupBounds(components.filter(c => topComponents.includes(c.id))),
  } : undefined;

  const bottomSection = bottomComponents.length > 0 ? {
    components: bottomComponents,
    bounds: calculateGroupBounds(components.filter(c => bottomComponents.includes(c.id))),
  } : undefined;

  return {
    canvasWidth,
    canvasHeight,
    componentCount: components.length,
    componentTypes,
    leftColumn,
    rightColumn,
    topSection,
    bottomSection,
  };
}

function calculateGroupBounds(components: PlacedComponent[]): { x: number; y: number; width: number; height: number } {
  if (components.length === 0) {
    return { x: 0, y: 0, width: 0, height: 0 };
  }

  const minX = Math.min(...components.map(c => c.x));
  const minY = Math.min(...components.map(c => c.y));
  const maxX = Math.max(...components.map(c => c.x + c.width));
  const maxY = Math.max(...components.map(c => c.y + c.height));

  return {
    x: minX,
    y: minY,
    width: maxX - minX,
    height: maxY - minY,
  };
}

function generateDescription(components: PlacedComponent[], stats: LayoutStats, relationships: SpatialRelationship[]): string {
  const parts: string[] = [];

  parts.push(`The sketch contains ${stats.componentCount} components:`);

  Object.entries(stats.componentTypes).forEach(([type, count]) => {
    parts.push(`- ${count} ${type}${count > 1 ? 's' : ''}`);
  });

  if (stats.leftColumn && stats.rightColumn) {
    parts.push(`The layout has two columns: left column with ${stats.leftColumn.components.length} components, right column with ${stats.rightColumn.components.length} components.`);
  }

  if (stats.topSection && stats.bottomSection) {
    parts.push(`The layout is divided into top section (${stats.topSection.components.length} components) and bottom section (${stats.bottomSection.components.length} components).`);
  }

  const alignmentCount = relationships.filter(r => r.relationship === 'aligned').length;
  if (alignmentCount > 0) {
    parts.push(`There are ${alignmentCount} aligned component pairs.`);
  }

  return parts.join(' ');
}

