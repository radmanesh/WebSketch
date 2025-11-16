'use client';

import { useRef, useEffect, useState } from 'react';
import { Stage, Layer, Rect, Transformer } from 'react-konva';
import type { KonvaStage, KonvaRect, KonvaTransformer, KonvaEventObject } from '@/types/konva';
import { PlacedComponent, Mode } from '@/types/types';
import PlacedComponentShape from './PlacedComponentShape';

interface CanvasContainerProps {
  components: PlacedComponent[];
  selectedId: string | null;
  mode: Mode;
  onBoxDrawn: (box: { x: number; y: number; width: number; height: number }) => void;
  onSelectComponent: (id: string | null) => void;
  onMove: (id: string, x: number, y: number) => void;
  onResize: (id: string, width: number, height: number, x: number, y: number) => void;
  onStageRef?: (stage: KonvaStage | null) => void;
}

export default function CanvasContainer({
  components,
  selectedId,
  mode,
  onBoxDrawn,
  onSelectComponent,
  onMove,
  onResize,
  onStageRef,
}: CanvasContainerProps) {
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });
  const [isDrawing, setIsDrawing] = useState(false);
  const [draftBox, setDraftBox] = useState<{ x: number; y: number; width: number; height: number } | null>(null);
  const [startPos, setStartPos] = useState({ x: 0, y: 0 });
  const containerRef = useRef<HTMLDivElement>(null);
  const transformerRef = useRef<KonvaTransformer>(null);
  const selectedShapeRef = useRef<KonvaRect | null>(null);
  const stageRef = useRef<KonvaStage | null>(null);

  useEffect(() => {
    if (typeof window !== 'undefined' && containerRef.current) {
      const updateDimensions = () => {
        const width = containerRef.current?.clientWidth || 800;
        const height = containerRef.current?.clientHeight || 600;
        setDimensions({ width, height });
      };

      updateDimensions();
      window.addEventListener('resize', updateDimensions);
      return () => window.removeEventListener('resize', updateDimensions);
    }
  }, []);

  useEffect(() => {
    if (transformerRef.current && selectedShapeRef.current) {
      transformerRef.current.nodes([selectedShapeRef.current]);
      transformerRef.current.getLayer()?.batchDraw();
    }
  }, [selectedId]);

  useEffect(() => {
    if (onStageRef) {
      onStageRef(stageRef.current);
      return () => onStageRef(null);
    }
  }, [onStageRef]);

  const handleMouseDown = (e: KonvaEventObject<MouseEvent>) => {
    if (mode !== 'draw') return;

    const stage = e.target.getStage();
    if (!stage) return;

    const pos = stage.getPointerPosition();
    if (!pos) return;

    setIsDrawing(true);
    setStartPos(pos);
    setDraftBox({ x: pos.x, y: pos.y, width: 0, height: 0 });
  };

  const handleMouseMove = (e: KonvaEventObject<MouseEvent>) => {
    if (!isDrawing || mode !== 'draw') return;

    const stage = e.target.getStage();
    if (!stage) return;

    const pos = stage.getPointerPosition();
    if (!pos) return;

    const width = pos.x - startPos.x;
    const height = pos.y - startPos.y;

    setDraftBox({
      x: width < 0 ? pos.x : startPos.x,
      y: height < 0 ? pos.y : startPos.y,
      width: Math.abs(width),
      height: Math.abs(height),
    });
  };

  const handleMouseUp = () => {
    if (!isDrawing || !draftBox || mode !== 'draw') return;

    // Only create component if box has meaningful size
    if (draftBox.width > 10 && draftBox.height > 10) {
      onBoxDrawn(draftBox);
    }

    setIsDrawing(false);
    setDraftBox(null);
  };

  const handleStageClick = (e: KonvaEventObject<MouseEvent>) => {
    if (mode === 'select') {
      const clickedOnEmpty = e.target === e.target.getStage();
      if (clickedOnEmpty) {
        onSelectComponent(null);
      }
    }
  };

  return (
    <div ref={containerRef} className="flex-1 bg-white overflow-hidden">
      <Stage
        ref={stageRef}
        width={dimensions.width}
        height={dimensions.height}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onClick={handleStageClick}
      >
        <Layer>
          {/* Render placed components */}
          {components.map((component) => (
            <PlacedComponentShape
              key={component.id}
              component={component}
              isSelected={component.id === selectedId}
              onSelect={() => onSelectComponent(component.id)}
              onMove={onMove}
              onResize={onResize}
              shapeRef={component.id === selectedId ? selectedShapeRef : undefined}
            />
          ))}

          {/* Render draft box when drawing */}
          {draftBox && mode === 'draw' && (
            <Rect
              x={draftBox.x}
              y={draftBox.y}
              width={draftBox.width}
              height={draftBox.height}
              fill="rgba(0, 123, 255, 0.15)"
              stroke="rgba(0, 123, 255, 0.6)"
              strokeWidth={2}
              dash={[5, 5]}
              opacity={0.7}
            />
          )}

          {/* Transformer for selected component */}
          {selectedId && mode === 'select' && <Transformer ref={transformerRef} />}
        </Layer>
      </Stage>
    </div>
  );
}
