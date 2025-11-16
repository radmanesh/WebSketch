'use client';

import { useEffect, useRef } from 'react';
import { Rect, Text, Group } from 'react-konva';
import type { KonvaRect, KonvaGroup } from '@/types/konva';
import { PlacedComponent } from '@/types/types';
import { componentManager } from '../manager/ComponentManager';

interface PlacedComponentShapeProps {
  component: PlacedComponent;
  isSelected: boolean;
  onSelect: () => void;
  onMove: (id: string, x: number, y: number) => void;
  onResize: (id: string, width: number, height: number, x: number, y: number) => void;
  shapeRef?: React.MutableRefObject<KonvaRect | null>;
}

export default function PlacedComponentShape({
  component,
  isSelected,
  onSelect,
  onMove,
  onResize,
  shapeRef,
}: PlacedComponentShapeProps) {
  const localRectRef = useRef<KonvaRect | null>(null);
  const rectRef = shapeRef || localRectRef;
  const groupRef = useRef<KonvaGroup | null>(null);

  useEffect(() => {
    if (rectRef.current) {
      rectRef.current.setAttrs({
        scaleX: 1,
        scaleY: 1,
      });
    }
  }, [component.width, component.height, rectRef]);

  // Sync Group position with component position when props change
  useEffect(() => {
    if (groupRef.current) {
      groupRef.current.position({ x: component.x, y: component.y });
    }
  }, [component.x, component.y]);

  const handleDragEnd = () => {
    const group = groupRef.current;
    if (!group) return;
    onMove(component.id, group.x(), group.y());
  };

  const handleTransformEnd = () => {
    const node = rectRef.current;
    const group = groupRef.current;
    if (!node || !group) return;

    const scaleX = node.scaleX();
    const scaleY = node.scaleY();

    // Get the current group position before resetting
    const currentGroupX = group.x();
    const currentGroupY = group.y();

    // Reset scale to 1
    node.scaleX(1);
    node.scaleY(1);

    // For HorizontalLine, enforce minimum height of 2px
    const minHeight = component.type === 'HorizontalLine' ? 2 : 20;
    const newWidth = Math.max(20, node.width() * scaleX);
    const newHeight = Math.max(minHeight, node.height() * scaleY);

    // Ensure the node's position within the group stays at 0,0
    node.position({ x: 0, y: 0 });

    // Ensure the group position hasn't been affected by transformer
    if (Math.abs(group.x() - currentGroupX) > 0.1 || Math.abs(group.y() - currentGroupY) > 0.1) {
      group.position({ x: currentGroupX, y: currentGroupY });
    }

    // Update with the current group position (which might have been adjusted by transformer)
    onResize(component.id, newWidth, newHeight, currentGroupX, currentGroupY);
  };

  // Get renderer for component type
  const renderer = componentManager.getRenderer(component.type);

  // Get component configuration
  const hasBorder = componentManager.hasBorder(component.type);
  const strokeColor = componentManager.getStrokeColor(component.type);
  const fillColor = componentManager.getFillColor(component.type);
  const contentStrokeColor = componentManager.getContentStrokeColor(component.type);

  // Render wireframe content
  const wireframeContent = renderer
    ? renderer.render({
        component,
        isSelected,
        width: component.width,
        height: component.height,
        strokeColor: contentStrokeColor,
      })
    : null;

  // For HorizontalLine, ensure minimum height
  const effectiveHeight = component.type === 'HorizontalLine'
    ? Math.max(component.height, 2)
    : component.height;

  return (
    <Group
      ref={groupRef}
      x={component.x}
      y={component.y}
      draggable={true}
      onClick={onSelect}
      onTap={onSelect}
      onDragEnd={handleDragEnd}
    >
      <Rect
        ref={rectRef}
        x={0}
        y={0}
        width={component.width}
        height={effectiveHeight}
        fill={component.type === 'HorizontalLine' ? 'transparent' : fillColor}
        stroke={hasBorder ? strokeColor : undefined}
        strokeWidth={hasBorder ? (isSelected ? 3 : 2) : 0}
        opacity={1}
        onTransformEnd={handleTransformEnd}
      />

      {/* Wireframe content */}
      {wireframeContent && (
        <Group x={0} y={0} listening={false}>
          {wireframeContent}
        </Group>
      )}

      {/* Component label - only for Button and Input */}
      {component.type === 'Button' && (
        <Text
          x={8}
          y={8}
          text="btn"
          fontSize={14}
          fill="#333333"
          opacity={0.9}
          listening={false}
        />
      )}
      {component.type === 'Input' && (
        <Text
          x={8}
          y={8}
          text="input"
          fontSize={14}
          fill="#333333"
          opacity={0.9}
          listening={false}
        />
      )}
    </Group>
  );
}
