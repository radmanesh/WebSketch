import { PlacedComponent } from '@/types/types';
import { ComponentOperation } from './schemas';

export function executeOperations(
  currentSketch: PlacedComponent[],
  operations: ComponentOperation[]
): PlacedComponent[] {
  let sketch = [...currentSketch];

  for (const operation of operations) {
    switch (operation.type) {
      case 'move':
        sketch = executeMove(sketch, operation);
        break;
      case 'resize':
        sketch = executeResize(sketch, operation);
        break;
      case 'add':
        sketch = executeAdd(sketch, operation);
        break;
      case 'delete':
        sketch = executeDelete(sketch, operation);
        break;
      case 'modify':
        sketch = executeModify(sketch, operation);
        break;
      case 'align':
        sketch = executeAlign(sketch, operation);
        break;
      case 'distribute':
        sketch = executeDistribute(sketch, operation);
        break;
    }
  }

  return sketch;
}

function executeMove(sketch: PlacedComponent[], operation: ComponentOperation): PlacedComponent[] {
  if (!operation.componentId || operation.x === undefined || operation.y === undefined) {
    return sketch;
  }

  return sketch.map(comp =>
    comp.id === operation.componentId
      ? { ...comp, x: operation.x!, y: operation.y! }
      : comp
  );
}

function executeResize(sketch: PlacedComponent[], operation: ComponentOperation): PlacedComponent[] {
  if (!operation.componentId || operation.width === undefined || operation.height === undefined) {
    return sketch;
  }

  const minWidth = 20;
  const minHeight = 20;

  return sketch.map(comp => {
    if (comp.id === operation.componentId) {
      const width = Math.max(minWidth, operation.width!);
      const height = comp.type === 'HorizontalLine'
        ? Math.max(2, operation.height!)
        : Math.max(minHeight, operation.height!);
      return { ...comp, width, height };
    }
    return comp;
  });
}

function executeAdd(sketch: PlacedComponent[], operation: ComponentOperation): PlacedComponent[] {
  if (!operation.componentType || operation.x === undefined || operation.y === undefined ||
      operation.width === undefined || operation.height === undefined) {
    return sketch;
  }

  const newId = `component-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  const minWidth = 20;
  const minHeight = 20;

  const newComponent: PlacedComponent = {
    id: newId,
    type: operation.componentType as any,
    x: operation.x,
    y: operation.y,
    width: Math.max(minWidth, operation.width),
    height: operation.componentType === 'HorizontalLine'
      ? Math.max(2, operation.height)
      : Math.max(minHeight, operation.height),
    props: operation.props || {},
  };

  return [...sketch, newComponent];
}

function executeDelete(sketch: PlacedComponent[], operation: ComponentOperation): PlacedComponent[] {
  if (!operation.componentId) {
    return sketch;
  }

  return sketch.filter(comp => comp.id !== operation.componentId);
}

function executeModify(sketch: PlacedComponent[], operation: ComponentOperation): PlacedComponent[] {
  if (!operation.componentId || !operation.props) {
    return sketch;
  }

  return sketch.map(comp =>
    comp.id === operation.componentId
      ? { ...comp, props: { ...comp.props, ...operation.props } }
      : comp
  );
}

function executeAlign(sketch: PlacedComponent[], operation: ComponentOperation): PlacedComponent[] {
  if (!operation.targetIds || !operation.alignment || operation.targetIds.length < 2) {
    return sketch;
  }

  const targetComponents = sketch.filter(comp => operation.targetIds!.includes(comp.id));
  if (targetComponents.length < 2) {
    return sketch;
  }

  let alignedValue: number;

  switch (operation.alignment) {
    case 'left':
      alignedValue = Math.min(...targetComponents.map(c => c.x));
      return sketch.map(comp =>
        operation.targetIds!.includes(comp.id)
          ? { ...comp, x: alignedValue }
          : comp
      );
    case 'right':
      alignedValue = Math.max(...targetComponents.map(c => c.x + c.width));
      return sketch.map(comp =>
        operation.targetIds!.includes(comp.id)
          ? { ...comp, x: alignedValue - comp.width }
          : comp
      );
    case 'center':
      alignedValue = targetComponents.reduce((sum, c) => sum + c.x + c.width / 2, 0) / targetComponents.length;
      return sketch.map(comp =>
        operation.targetIds!.includes(comp.id)
          ? { ...comp, x: alignedValue - comp.width / 2 }
          : comp
      );
    case 'top':
      alignedValue = Math.min(...targetComponents.map(c => c.y));
      return sketch.map(comp =>
        operation.targetIds!.includes(comp.id)
          ? { ...comp, y: alignedValue }
          : comp
      );
    case 'bottom':
      alignedValue = Math.max(...targetComponents.map(c => c.y + c.height));
      return sketch.map(comp =>
        operation.targetIds!.includes(comp.id)
          ? { ...comp, y: alignedValue - comp.height }
          : comp
      );
    default:
      return sketch;
  }
}

function executeDistribute(sketch: PlacedComponent[], operation: ComponentOperation): PlacedComponent[] {
  if (!operation.targetIds || operation.spacing === undefined || operation.targetIds.length < 2) {
    return sketch;
  }

  const targetComponents = sketch.filter(comp => operation.targetIds!.includes(comp.id));
  if (targetComponents.length < 2) {
    return sketch;
  }

  // Sort by x position for horizontal distribution
  const sorted = [...targetComponents].sort((a, b) => a.x - b.x);
  const firstX = sorted[0].x;
  let currentX = firstX;

  const updatedComponents = sorted.map(comp => {
    const updated = { ...comp, x: currentX };
    currentX += comp.width + operation.spacing!;
    return updated;
  });

  return sketch.map(comp => {
    const updated = updatedComponents.find(uc => uc.id === comp.id);
    return updated || comp;
  });
}

