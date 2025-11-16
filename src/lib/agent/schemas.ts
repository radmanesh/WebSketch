// JSON Schema definitions for structured output (no Zod dependency)
export interface ComponentOperation {
  type: 'move' | 'resize' | 'add' | 'delete' | 'modify' | 'align' | 'distribute';
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

// JSON Schema for OpenAI structured output
export const SketchModificationJSONSchema = {
  type: 'object',
  properties: {
    operations: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          type: {
            type: 'string',
            enum: ['move', 'resize', 'add', 'delete', 'modify', 'align', 'distribute'],
          },
          componentId: { type: 'string' },
          componentType: { type: 'string' },
          x: { type: 'number' },
          y: { type: 'number' },
          width: { type: 'number' },
          height: { type: 'number' },
          props: { type: 'object' },
          targetIds: {
            type: 'array',
            items: { type: 'string' },
          },
          alignment: {
            type: 'string',
            enum: ['left', 'right', 'center', 'top', 'bottom'],
          },
          spacing: { type: 'number' },
        },
        required: ['type'],
      },
    },
    reasoning: {
      type: 'string',
      description: 'Brief explanation of why these operations were chosen',
    },
    description: {
      type: 'string',
      description: 'Human-readable description of what will change',
    },
  },
  required: ['operations', 'reasoning', 'description'],
  additionalProperties: false,
} as const;

