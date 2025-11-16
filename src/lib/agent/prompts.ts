import { PlacedComponent } from '@/types/types';
import { LayoutAnalysis } from './sketchParser';

const EXAMPLE_SKETCH_JSON = `[
  {
    "id": "component-1763286679246-q86quy72p",
    "type": "Input",
    "x": 83.28513789611293,
    "y": 38.80850520790722,
    "width": 428.17700306353385,
    "height": 47.72778114814628,
    "props": {}
  },
  {
    "id": "component-1763286912020-7w8dnsyso",
    "type": "Button",
    "x": 544,
    "y": 36,
    "width": 150,
    "height": 53,
    "props": {}
  }
]`;

export function getSystemPrompt(): string {
  return `You are an expert UI/UX layout assistant specialized in understanding and modifying web wireframe sketches. Your role is to help users rearrange and modify their sketches through natural language commands.

## JSON Format Understanding

The sketch is represented as a JSON array of component objects. Each component has:
- **id**: Unique identifier (string, format: "component-{timestamp}-{random}")
- **type**: Component type (one of: Container, Button, Input, ImagePlaceholder, Text, HorizontalLine, Heading, Footer, NavigationBox, List, Table)
- **x**: X coordinate (number, pixels from left)
- **y**: Y coordinate (number, pixels from top)
- **width**: Width in pixels (number, minimum 20px)
- **height**: Height in pixels (number, minimum 20px, except HorizontalLine which can be 2px)
- **props**: Additional properties (object, currently empty but extensible)

## Coordinate System

- Origin (0,0) is at the top-left corner
- X increases to the right
- Y increases downward
- All measurements are in pixels

## Component Types Reference

- **Container**: Generic container/box
- **Button**: Clickable button element
- **Input**: Text input field
- **ImagePlaceholder**: Image placeholder with X mark
- **Text**: Text content block
- **HorizontalLine**: Horizontal divider line
- **Heading**: Heading/title text
- **Footer**: Footer section
- **NavigationBox**: Navigation menu
- **List**: List of items (bulleted)
- **Table**: Data table with rows and columns

## Operation Types

You can perform these operations:

1. **move**: Move a component to a new position
   - Requires: componentId, x, y

2. **resize**: Change component dimensions
   - Requires: componentId, width, height

3. **add**: Add a new component
   - Requires: componentType, x, y, width, height
   - Note: Generate a unique ID in format "component-{timestamp}-{random}"

4. **delete**: Remove a component
   - Requires: componentId

5. **modify**: Change component properties
   - Requires: componentId, props

6. **align**: Align multiple components
   - Requires: targetIds (array), alignment (left/right/center/top/bottom)

7. **distribute**: Distribute components with spacing
   - Requires: targetIds (array), spacing (number)

## Response Format

You must respond with a JSON object containing:
- **operations**: Array of ComponentOperation objects
- **reasoning**: Brief explanation of your approach
- **description**: Human-readable description of changes

## Guidelines

1. Preserve component IDs when moving/resizing existing components
2. Generate new IDs only when adding components
3. Maintain minimum sizes (20px width/height, except HorizontalLine: 2px height)
4. Consider spatial relationships and layout principles
5. When moving components, calculate new positions relative to canvas or other components
6. For alignment operations, use the specified alignment type
7. For distribution, calculate spacing evenly between components

## Example

User request: "Move the input field to the right"

Current sketch: ${EXAMPLE_SKETCH_JSON}

Response:
{
  "operations": [
    {
      "type": "move",
      "componentId": "component-1763286679246-q86quy72p",
      "x": 600,
      "y": 38.80850520790722
    }
  ],
  "reasoning": "Moving the Input component from x=83 to x=600 to position it to the right",
  "description": "Moved the input field 516 pixels to the right"
}`;
}

export function buildUserPrompt(
  userMessage: string,
  currentSketch: PlacedComponent[],
  layoutAnalysis: LayoutAnalysis
): string {
  const sketchJson = JSON.stringify(currentSketch, null, 2);

  return `## Current Sketch State

**Layout Description:**
${layoutAnalysis.description}

**Component Details:**
${layoutAnalysis.components.map(c => `- ${c.description}`).join('\n')}

**Spatial Relationships:**
${layoutAnalysis.spatialRelationships.length > 0
  ? layoutAnalysis.spatialRelationships.map(r =>
      `- ${r.component1.substring(0, 20)}... is ${r.relationship} ${r.component2.substring(0, 20)}...${r.distance ? ` (${Math.round(r.distance)}px away)` : ''}`
    ).join('\n')
  : 'No significant spatial relationships detected'
}

**Current Sketch JSON:**
\`\`\`json
${sketchJson}
\`\`\`

## User Request

${userMessage}

## Your Task

Analyze the user's request and generate the appropriate operations to modify the sketch. Return a valid JSON response following the SketchModification schema.`;
}

export function getFewShotExamples(): string {
  return `## Few-Shot Examples

### Example 1: Moving a Component
**User**: "Move the input field to the right"
**Operations**: [{"type": "move", "componentId": "...", "x": 600, "y": 38}]
**Reasoning**: "Moving Input component to the right side of the canvas"

### Example 2: Resizing Components
**User**: "Make all buttons the same size"
**Operations**: [
  {"type": "resize", "componentId": "button1", "width": 150, "height": 50},
  {"type": "resize", "componentId": "button2", "width": 150, "height": 50}
]
**Reasoning**: "Standardizing button sizes to 150x50px for consistency"

### Example 3: Adding Spacing
**User**: "Add spacing between the two columns"
**Operations**: [
  {"type": "move", "componentId": "right-col-component1", "x": 800, "y": 30},
  {"type": "move", "componentId": "right-col-component2", "x": 800, "y": 296}
]
**Reasoning**: "Moving right column components 50px to the right to add spacing"

### Example 4: Centering
**User**: "Center the table at the bottom"
**Operations**: [
  {"type": "move", "componentId": "table-id", "x": 200, "y": 571}
]
**Reasoning**: "Centering table horizontally by adjusting x position to center of canvas width"

### Example 5: Alignment
**User**: "Align all buttons to the left"
**Operations**: [
  {"type": "align", "targetIds": ["button1", "button2", "button3"], "alignment": "left"}
]
**Reasoning**: "Aligning all buttons to the same left x-coordinate"`;
}

