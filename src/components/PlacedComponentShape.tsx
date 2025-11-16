'use client';

import { useEffect, useRef } from 'react';
import { Rect, Text, Group, Line, Path, Circle } from 'react-konva';
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

// Components that should have borders
const COMPONENTS_WITH_BORDERS: ComponentType[] = [
  'Container',
  'Button',
  'Input',
  'ImagePlaceholder',
  'NavigationBox',
];

const getComponentHasBorder = (type: ComponentType): boolean => {
  return COMPONENTS_WITH_BORDERS.includes(type);
};

// All components get very transparent background for display visibility
const getComponentColor = (type: ComponentType): string => {
  // Very transparent background for all components (display only, not exported)
  return 'rgba(128, 128, 128, 0.1)'; // Light gray with 10% opacity
};

const getComponentStroke = (type: ComponentType): string => {
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
  const groupRef = useRef<Konva.Group | null>(null);

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

  const renderWireframeContent = () => {
    const { type, width, height } = component;
    // Get stroke color for wireframe content (not container border)
    let strokeColor = getComponentStroke(type);

    // Override for content-specific colors (not border colors)
    if (type === 'Text') {
      strokeColor = '#808080'; // Gray for wavy lines
    } else if (type === 'Heading' || type === 'List') {
      strokeColor = '#000000'; // Black for bold/wavy lines
    } else if (type === 'Footer' || type === 'Table' || type === 'HorizontalLine') {
      strokeColor = '#666666'; // Medium gray
    }

    switch (type) {
      case 'Text': {
        // Wavy horizontal lines
        const lines: JSX.Element[] = [];
        const lineSpacing = 20;
        const waveAmplitude = 3;
        const waveLength = 30;
        let currentY = 15;

        while (currentY < height - 10) {
          const points: number[] = [];
          for (let xPos = 10; xPos < width - 10; xPos += 2) {
            const waveY = Math.sin((xPos / waveLength) * Math.PI * 2) * waveAmplitude;
            points.push(xPos, currentY + waveY);
          }
          lines.push(
            <Line
              key={currentY}
              points={points}
              stroke={strokeColor}
              strokeWidth={1.5}
              tension={0.5}
              listening={false}
            />
          );
          currentY += lineSpacing;
        }
        return lines;
      }

      case 'HorizontalLine': {
        // Single horizontal line - rendered as content overlay
        const centerY = Math.max(height, 2) / 2;
        return (
          <Line
            points={[0, centerY, width, centerY]}
            stroke={strokeColor}
            strokeWidth={2}
            listening={false}
          />
        );
      }

      case 'Heading': {
        // Bold straight lines - draw multiple bold lines based on height like Text
        const lines: JSX.Element[] = [];
        const lineSpacing = 25;
        const lineThickness = 4;
        let currentY = 15;

        while (currentY < height - 10) {
          lines.push(
            <Line
              key={currentY}
              points={[10, currentY, width - 10, currentY]}
              stroke="#000000"
              strokeWidth={lineThickness}
              listening={false}
            />
          );
          currentY += lineSpacing;
        }
        return lines;
      }

      case 'NavigationBox': {
        // Box with hamburger icon (3 horizontal lines)
        const lines: JSX.Element[] = [];
        const iconSize = Math.min(20, width - 20, height - 20);
        const iconX = 10;
        const iconY = 10;
        const lineSpacing = iconSize / 4;
        const lineWidth = iconSize * 0.6;

        // Three horizontal lines for hamburger
        for (let i = 0; i < 3; i++) {
          lines.push(
            <Line
              key={`hamburger-${i}`}
              points={[iconX, iconY + i * lineSpacing, iconX + lineWidth, iconY + i * lineSpacing]}
              stroke={strokeColor}
              strokeWidth={2}
              listening={false}
            />
          );
        }
        return lines;
      }

      case 'List': {
        // Repeated wavy horizontal lines with circles in front
        const elements: JSX.Element[] = [];
        const lineSpacing = 25;
        const circleRadius = 4;
        const circleX = 15;
        const waveAmplitude = 2;
        const waveLength = 20;
        let currentY = 15;

        while (currentY < height - 10) {
          // Circle
          elements.push(
            <Circle
              key={`circle-${currentY}`}
              x={circleX}
              y={currentY}
              radius={circleRadius}
              stroke={strokeColor}
              strokeWidth={2}
              fill="transparent"
              listening={false}
            />
          );
          // Wavy line instead of straight
          const lineStartX = circleX + circleRadius + 8;
          const points: number[] = [];
          for (let xPos = lineStartX; xPos < width - 10; xPos += 2) {
            const waveY = Math.sin((xPos / waveLength) * Math.PI * 2) * waveAmplitude;
            points.push(xPos, currentY + waveY);
          }
          if (points.length > 0) {
            elements.push(
              <Line
                key={`line-${currentY}`}
                points={points}
                stroke={strokeColor}
                strokeWidth={2}
                tension={0.5}
                listening={false}
              />
            );
          }
          currentY += lineSpacing;
        }
        return elements;
      }

      case 'Table': {
        // Grid pattern with horizontal and vertical lines
        const lines: JSX.Element[] = [];
        const rowCount = Math.max(2, Math.floor(height / 30));
        const colCount = Math.max(2, Math.floor(width / 80));
        const rowHeight = height / rowCount;
        const colWidth = width / colCount;

        // Horizontal lines
        for (let i = 0; i <= rowCount; i++) {
          lines.push(
            <Line
              key={`h-${i}`}
              points={[0, i * rowHeight, width, i * rowHeight]}
              stroke={strokeColor}
              strokeWidth={1.5}
              listening={false}
            />
          );
        }

        // Vertical lines
        for (let i = 0; i <= colCount; i++) {
          lines.push(
            <Line
              key={`v-${i}`}
              points={[i * colWidth, 0, i * colWidth, height]}
              stroke={strokeColor}
              strokeWidth={1.5}
              listening={false}
            />
          );
        }
        return lines;
      }

      case 'ImagePlaceholder': {
        // Rectangle with X mark
        const centerX = width / 2;
        const centerY = height / 2;
        const xSize = Math.min(width, height) * 0.3;
        return (
          <>
            <Line
              points={[centerX - xSize, centerY - xSize, centerX + xSize, centerY + xSize]}
              stroke={strokeColor}
              strokeWidth={3}
              listening={false}
            />
            <Line
              points={[centerX - xSize, centerY + xSize, centerX + xSize, centerY - xSize]}
              stroke={strokeColor}
              strokeWidth={3}
              listening={false}
            />
          </>
        );
      }

      case 'Footer': {
        // Box (not wavy) - just the rect with label, no special pattern
        return null;
      }

      default:
        return null;
    }
  };

  // For HorizontalLine, ensure minimum height
  const effectiveHeight = component.type === 'HorizontalLine'
    ? Math.max(component.height, 2)
    : component.height;

  const hasBorder = getComponentHasBorder(component.type);
  const strokeColor = hasBorder ? getComponentStroke(component.type) : undefined;

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
        fill={component.type === 'HorizontalLine' ? 'transparent' : getComponentColor(component.type)}
        stroke={strokeColor}
        strokeWidth={hasBorder ? (isSelected ? 3 : 2) : 0}
        opacity={component.type === 'HorizontalLine' ? 1 : 1}
        onTransformEnd={handleTransformEnd}
      />

      {/* Wireframe content */}
      <Group x={0} y={0} listening={false}>
        {renderWireframeContent()}
      </Group>

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
