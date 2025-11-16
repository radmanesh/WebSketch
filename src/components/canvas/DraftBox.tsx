import { Rect } from 'react-konva';

interface DraftBoxProps {
  x: number;
  y: number;
  width: number;
  height: number;
}

/**
 * Draft box component shown during drawing
 */
export default function DraftBox({ x, y, width, height }: DraftBoxProps) {
  return (
    <Rect
      x={x}
      y={y}
      width={width}
      height={height}
      fill="rgba(0, 123, 255, 0.15)"
      stroke="rgba(0, 123, 255, 0.6)"
      strokeWidth={2}
      dash={[5, 5]}
      opacity={0.7}
    />
  );
}
