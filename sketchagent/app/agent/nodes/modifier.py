"""Modifier agent node - generates operations from user intent"""

import json
from ..state import AgentState
from ...schemas.sketch import SketchModification, ComponentOperation
from ...services.llm_service import LLMService
from ...utils.logger import get_logger
from ...utils.errors import LLMError

logger = get_logger(__name__)

EXAMPLE_SKETCH_JSON = """[
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
]"""


def get_system_prompt() -> str:
    """Get system prompt for LLM"""
    return """You are an expert UI/UX layout assistant specialized in understanding and modifying web wireframe sketches. Your role is to help users rearrange and modify their sketches through natural language commands.

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

You must respond with a valid JSON object matching this schema:
{
  "operations": [
    {
      "type": "move|resize|add|delete|modify|align|distribute",
      "componentId": "string (optional)",
      "componentType": "string (optional, for add)",
      "x": "number (optional)",
      "y": "number (optional)",
      "width": "number (optional)",
      "height": "number (optional)",
      "props": "object (optional)",
      "targetIds": "array of strings (optional)",
      "alignment": "left|right|center|top|bottom (optional)",
      "spacing": "number (optional)"
    }
  ],
  "reasoning": "Brief explanation of why these operations were chosen",
  "description": "Human-readable description of what will change"
}

## Guidelines

1. Preserve component IDs when moving/resizing existing components
2. Generate new IDs only when adding components (format: "component-{timestamp}-{random}")
3. Maintain minimum sizes (20px width/height, except HorizontalLine: 2px height)
4. Consider spatial relationships and layout principles
5. When moving components, calculate new positions relative to canvas or other components
6. For alignment operations, use the specified alignment type
7. For distribution, calculate spacing evenly between components
8. Respond ONLY with valid JSON, no markdown formatting or code blocks"""


def build_user_prompt(state: AgentState) -> str:
    """Build user prompt with context"""
    layout_analysis = state["layout_analysis"]
    sketch_json = json.dumps(
        [comp.model_dump() for comp in state["current_sketch"]], indent=2
    )

    relationships_text = "No significant spatial relationships detected"
    if layout_analysis and layout_analysis.get("spatialRelationships"):
        rels = layout_analysis["spatialRelationships"]
        relationships_text = "\n".join(
            f"- {r['component1'][:20]}... is {r['relationship']} {r['component2'][:20]}..."
            + (f" ({int(r.get('distance', 0))}px away)" if r.get("distance") else "")
            for r in rels
        )

    components_text = ""
    if layout_analysis and layout_analysis.get("components"):
        components_text = "\n".join(
            f"- {c['description']}" for c in layout_analysis["components"]
        )

    return f"""## Current Sketch State

**Layout Description:**
{layout_analysis['description'] if layout_analysis else 'No layout analysis available'}

**Component Details:**
{components_text}

**Spatial Relationships:**
{relationships_text}

**Current Sketch JSON:**
```json
{sketch_json}
```

## User Request

{state['user_message']}

## Your Task

Analyze the user's request and generate the appropriate operations to modify the sketch. Return a valid JSON response following the schema above."""


async def modify_node(state: AgentState, llm_service: LLMService) -> AgentState:
    """Generate modification operations from user intent"""
    logger.info("Generating modifications", session_id=state["session_id"])

    try:
        system_prompt = get_system_prompt()
        user_prompt = build_user_prompt(state)

        # Call LLM
        response_text = await llm_service.invoke(
            system_prompt, user_prompt, state["session_id"]
        )

        # Parse JSON response
        # Try to extract JSON from markdown code blocks if present
        content = response_text
        json_match = None
        if "```" in content:
            import re
            json_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", content)
            if json_match:
                content = json_match.group(1)

        # Parse JSON
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError as e:
            raise LLMError(f"Failed to parse JSON response: {str(e)}", state["session_id"])

        # Validate and create modification
        modification = SketchModification(**parsed)
        operations = [
            ComponentOperation(**op) if isinstance(op, dict) else op
            for op in modification.operations
        ]

        state["modification"] = modification
        state["operations"] = operations
        state["step"] = "validate"

        logger.info(
            "Modification generated",
            session_id=state["session_id"],
            operation_count=len(operations),
        )
    except Exception as e:
        logger.error("Modification generation failed", error=str(e), session_id=state["session_id"])
        state["step"] = "error"
        state["error"] = f"Modification generation failed: {str(e)}"

    return state

