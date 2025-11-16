/**
 * Centralized Konva type exports
 * This prevents multiple Konva instances from being created
 */
import type Konva from 'konva';

export type KonvaStage = Konva.Stage;
export type KonvaRect = Konva.Rect;
export type KonvaGroup = Konva.Group;
export type KonvaTransformer = Konva.Transformer;
export type KonvaEventObject<T> = Konva.KonvaEventObject<T>;

