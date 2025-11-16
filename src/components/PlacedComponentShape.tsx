'use client';

import { useEffect, useRef } from 'react';
import { Rect, Text, Group } from 'react-konva';
import Konva from 'konva';
import { PlacedComponent, ComponentType } from '@/types/types';

interface PlacedComponentShapeProps {
  component: PlacedComponent;
  isSelected: boolean;
  onSelect: () => void;
  onMove: (id: string, x: number, y: number) => void;
  onResize: (id: string, width: number, height: number, x: number, y: number) => void;
  shapeRef?: React.MutableRefObject<Konva.Rect | null>;
}

const getComponentColor = (type: ComponentType): string => {
  switch (type) {
    case 'Container':
      return '#e3f2fd';
    case 'Button':
      return '#f3e5f5';
    case 'Input':
      return '#fff3e0';
    case 'ImagePlaceholder':
      return '#e8f5e9';
    default:
      return '#f5f5f5';
  }
};

const getComponentStroke = (type: ComponentType): string => {
  switch (type) {
    case 'Container':
      return '#2196f3';
    case 'Button':
      return '#9c27b0';
    case 'Input':
      return '#ff9800';
    case 'ImagePlaceholder':
      return '#4caf50';
    default:
      return '#757575';
  }
};

export default function PlacedComponentShape({
  component,
  isSelected,
  onSelect,
  onMove,
  onResize,
  shapeRef,
}: PlacedComponentShapeProps) {
  const localRectRef = useRef<Konva.Rect | null>(null);
  const rectRef = shapeRef || localRectRef;

  useEffect(() => {
    if (rectRef.current) {
      rectRef.current.setAttrs({
        scaleX: 1,
        scaleY: 1,
      });
    }
  }, [component.width, component.height, rectRef]);

  const handleDragEnd = () => {
    const node = rectRef.current;
    if (!node) return;
    onMove(component.id, node.x(), node.y());
  };

  const handleTransformEnd = () => {
    const node = rectRef.current;
    if (!node) return;

    const scaleX = node.scaleX();
    const scaleY = node.scaleY();

    // Reset scale to 1
    node.scaleX(1);
    node.scaleY(1);

    const newWidth = Math.max(20, node.width() * scaleX);
    const newHeight = Math.max(20, node.height() * scaleY);

    onResize(component.id, newWidth, newHeight, node.x(), node.y());
  };

  return (
    <Group>
      <Rect
        ref={rectRef}
        x={component.x}
        y={component.y}
        width={component.width}
        height={component.height}
        fill={getComponentColor(component.type)}
        stroke={getComponentStroke(component.type)}
        strokeWidth={isSelected ? 3 : 2}
        draggable={true}
        onClick={onSelect}
        onTap={onSelect}
        onDragEnd={handleDragEnd}
        onTransformEnd={handleTransformEnd}
      />
      <Text
        x={component.x + 8}
        y={component.y + 8}
        text={component.type}
        fontSize={14}
        fill="#333"
        listening={false}
      />
    </Group>
  );
}
