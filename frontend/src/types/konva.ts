/**
 * Centralized Konva type exports
 * This prevents multiple Konva instances from being created
 * Types are extracted from react-konva components to avoid importing konva directly
 */
import type { Stage, Rect, Group, Transformer } from 'react-konva';
import type React from 'react';

// Extract types from react-konva component refs to avoid importing konva directly
export type KonvaStage = React.ComponentRef<typeof Stage>;
export type KonvaRect = React.ComponentRef<typeof Rect>;
export type KonvaGroup = React.ComponentRef<typeof Group>;
export type KonvaTransformer = React.ComponentRef<typeof Transformer>;

// Extract event type from Stage component's event handler props
type StageProps = React.ComponentProps<typeof Stage>;
type MouseDownHandler = NonNullable<StageProps['onMouseDown']>;
export type KonvaEventObject<T> = Parameters<MouseDownHandler>[0];

