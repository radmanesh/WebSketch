"""Manual test script for testing agent with websketch1.json

Run this script to test the agent with real sketch data:
    python -m pytest tests/integration/test_real_sketch_manual.py -v -s

Or run directly:
    python tests/integration/test_real_sketch_manual.py
"""

import json
import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.agent.graph import create_agent_graph
from app.agent.state import AgentState
from app.schemas.sketch import PlacedComponent
from app.services.llm_service import LLMService
from app.config import settings


def load_websketch1() -> list:
    """Load the websketch1.json file"""
    data_dir = Path(__file__).parent.parent.parent / "data"
    json_file = data_dir / "websketch1.json"

    with open(json_file, "r") as f:
        return json.load(f)


async def test_move_input_to_right():
    """Test moving the input component to the right"""
    print("=" * 80)
    print("Testing Agent with websketch1.json - Move Input to Right")
    print("=" * 80)

    # Load real sketch data
    sketch_data = load_websketch1()
    print(f"\nLoaded sketch with {len(sketch_data)} components")

    # Find the input component
    input_component = None
    for comp in sketch_data:
        if comp.get("type") == "Input":
            input_component = comp
            break

    if not input_component:
        print("ERROR: No Input component found in sketch")
        return

    print(f"\nFound Input component:")
    print(f"  ID: {input_component['id']}")
    print(f"  Current position: x={input_component['x']}, y={input_component['y']}")

    # Calculate new position (move 200px to the right)
    original_x = input_component["x"]
    new_x = original_x + 200

    print(f"  Target position: x={new_x}, y={input_component['y']}")

    # Convert sketch data to PlacedComponent objects
    current_sketch = [PlacedComponent(**comp) for comp in sketch_data]

    # Create LLM service (will use real API if OPENAI_API_KEY is set)
    llm_service = LLMService(
        api_key=settings.openai_api_key,
        model_name=settings.openai_model,
        temperature=settings.openai_temperature,
    )

    # Create agent graph
    graph = create_agent_graph(llm_service)

    # Initialize state
    initial_state: AgentState = {
        "session_id": "test-websketch1-manual",
        "user_message": "Move the input field to the right",
        "current_sketch": current_sketch,
        "message_history": None,
        "layout_analysis": None,
        "operations": None,
        "modification": None,
        "modified_sketch": None,
        "step": "analyze",
        "error": None,
        "initial_sketch": current_sketch.copy(),
        "latest_sketch": current_sketch.copy(),
        "retry_count": 0,
    }

    config = {"configurable": {"thread_id": "test-websketch1-manual"}}

    print("\n" + "=" * 80)
    print("Running agent workflow...")
    print("=" * 80)

    # Run graph
    final_state = None
    node_count = 0
    try:
        async for state_dict in graph.astream(initial_state, config):
            if isinstance(state_dict, dict):
                for node_name, node_state in state_dict.items():
                    if isinstance(node_state, dict):
                        final_state = node_state
                        node_count += 1
                        step = node_state.get("step", "unknown")
                        print(f"\n[{node_count}] Node: {node_name} -> Step: {step}")
                        if node_state.get("error"):
                            print(f"  ERROR: {node_state.get('error')}")
                        if node_state.get("operations"):
                            print(f"  Operations: {len(node_state.get('operations', []))}")
    except Exception as e:
        print(f"\nERROR during graph execution: {e}")
        import traceback
        traceback.print_exc()
        return

    # Results
    print("\n" + "=" * 80)
    print("Results")
    print("=" * 80)

    if not final_state:
        print("ERROR: Graph did not return a final state")
        return

    step = final_state.get("step")
    error = final_state.get("error")

    print(f"\nFinal Step: {step}")
    if error:
        print(f"Error: {error}")
        return

    modified_sketch = final_state.get("modified_sketch")
    if not modified_sketch:
        print("ERROR: No modified sketch in final state")
        return

    print(f"Modified sketch has {len(modified_sketch)} components")

    # Verify the input component was moved
    moved_input = None
    for comp in modified_sketch:
        if comp.id == input_component["id"]:
            moved_input = comp
            break

    if not moved_input:
        print("ERROR: Input component not found in modified sketch")
        return

    print(f"\nInput component after modification:")
    print(f"  ID: {moved_input.id}")
    print(f"  Position: x={moved_input.x}, y={moved_input.y}")
    print(f"  Original position: x={original_x}, y={input_component['y']}")

    if abs(moved_input.x - new_x) < 1.0:  # Allow small floating point differences
        print(f"\n✓ SUCCESS: Input component moved to x={moved_input.x} (target: {new_x})")
    else:
        print(f"\n⚠ WARNING: Input component at x={moved_input.x}, expected x={new_x}")
        print("  (This is expected if using real LLM - it may choose a different position)")

    # Show operations
    operations = final_state.get("operations", [])
    if operations:
        print(f"\nOperations executed: {len(operations)}")
        for i, op in enumerate(operations):
            if hasattr(op, "model_dump"):
                op_dict = op.model_dump()
            else:
                op_dict = op
            print(f"  [{i+1}] {op_dict.get('type')} - {op_dict.get('componentId', 'N/A')}")

    modification = final_state.get("modification")
    if modification:
        print(f"\nReasoning: {modification.reasoning}")
        print(f"Description: {modification.description}")


if __name__ == "__main__":
    asyncio.run(test_move_input_to_right())

