import { PlacedComponent } from './types';

export type ChatMessageRole = 'user' | 'assistant' | 'system';

export interface ChatMessage {
  role: ChatMessageRole;
  content: string;
  timestamp?: Date;
  imageUrl?: string; // URL for displaying uploaded image
  imageData?: string; // Base64 image data
}

export type ComponentOperationType =
  | 'move'
  | 'resize'
  | 'add'
  | 'delete'
  | 'modify'
  | 'align'
  | 'distribute';

export interface ComponentOperation {
  type: ComponentOperationType;
  componentId?: string;
  componentType?: string;
  x?: number;
  y?: number;
  width?: number;
  height?: number;
  props?: Record<string, unknown>;
  targetIds?: string[];
  alignment?: 'left' | 'right' | 'center' | 'top' | 'bottom';
  spacing?: number;
}

export interface SketchModification {
  operations: ComponentOperation[];
  reasoning: string;
  description: string;
}

export interface AgentResponse {
  modification: SketchModification;
  success: boolean;
  error?: string;
}

export interface ChatRequest {
  message: string;
  currentSketch: PlacedComponent[];
  messageHistory?: ChatMessage[];
}

