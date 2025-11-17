"""Integration tests using real sketch data"""

import json
import pytest
from pathlib import Path
from unittest.mock import AsyncMock
from app.agent.graph import create_agent_graph
from app.agent.state import AgentState
from app.services.llm_service import LLMService


def load_websketch1() -> list:
    """Load the websketch1.json file"""
    data_dir = Path(__file__).parent.parent.parent / "data"
    json_file = data_dir / "websketch1.json"

    with open(json_file, "r") as f:
        return json.load(f)


@pytest.mark.integration
class TestRealSketch:
    """Test agent with real sketch data from websketch1.json"""

    @pytest.mark.asyncio
    async def test_move_input_to_right(self, mock_llm_service):
        """Test moving the input component to the right using real sketch data"""
        # Load real sketch data
        sketch_data = load_websketch1()

        # Find the input component
        input_component = None
        for comp in sketch_data:
            if comp.get("type") == "Input":
                input_component = comp
                break

        assert input_component is not None, "No Input component found in sketch"

        # Calculate new position (move 200px to the right)
        original_x = input_component["x"]
        new_x = original_x + 200

        # Configure mock LLM to return a move operation
        mock_llm_service.invoke = AsyncMock(
            return_value=json.dumps({
                "operations": [
                    {
                        "type": "move",
                        "componentId": input_component["id"],
                        "x": new_x,
                        "y": input_component["y"]
                    }
                ],
                "reasoning": "Moving the input component 200 pixels to the right as requested",
                "description": "Input component moved to the right"
            })
        )

        # Convert sketch data to PlacedComponent objects
        from app.schemas.sketch import PlacedComponent
        current_sketch = [PlacedComponent(**comp) for comp in sketch_data]

        # Create agent graph
        graph = create_agent_graph(mock_llm_service)

        # Initialize state
        initial_state: AgentState = {
            "session_id": "test-websketch1",
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

        config = {"configurable": {"thread_id": "test-websketch1"}}

        # Run graph
        final_state = None
        try:
            async for state_dict in graph.astream(initial_state, config):
                if isinstance(state_dict, dict):
                    for node_name, node_state in state_dict.items():
                        if isinstance(node_state, dict):
                            final_state = node_state
                        else:
                            final_state = state_dict
        except KeyError as e:
            pytest.fail(f"Graph routing error: {e}")

        # Assertions
        assert final_state is not None, "Graph did not return a final state"
        assert final_state.get("step") in ["complete", "execute"], f"Expected step 'complete' or 'execute', got '{final_state.get('step')}'"
        assert final_state.get("error") is None, f"Unexpected error: {final_state.get('error')}"
        assert final_state.get("modified_sketch") is not None, "No modified sketch in final state"

        # Verify the input component was moved
        modified_sketch = final_state["modified_sketch"]
        moved_input = None
        for comp in modified_sketch:
            if comp.id == input_component["id"]:
                moved_input = comp
                break

        assert moved_input is not None, "Input component not found in modified sketch"
        assert moved_input.x == new_x, f"Expected x={new_x}, got x={moved_input.x}"
        assert moved_input.y == input_component["y"], f"Y coordinate should not change, got y={moved_input.y}"

        # Verify other components are unchanged
        original_ids = {comp["id"] for comp in sketch_data}
        modified_ids = {comp.id for comp in modified_sketch}
        assert original_ids == modified_ids, "Component IDs should match (no components added/removed)"

        # Verify component count is the same
        assert len(modified_sketch) == len(sketch_data), "Component count should remain the same"

    @pytest.mark.asyncio
    async def test_analyze_real_sketch(self, mock_llm_service):
        """Test analyzing the real sketch layout"""
        sketch_data = load_websketch1()
        from app.schemas.sketch import PlacedComponent
        from app.agent.nodes.analyzer import analyze_node

        current_sketch = [PlacedComponent(**comp) for comp in sketch_data]

        state: AgentState = {
            "session_id": "test-analyze",
            "user_message": "Analyze this sketch",
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

        result = analyze_node(state)

        assert result["step"] == "modify"
        assert result["layout_analysis"] is not None
        assert result["layout_analysis"]["layoutStats"]["componentCount"] == len(sketch_data)

        # Verify layout analysis has expected structure
        layout = result["layout_analysis"]
        assert "description" in layout
        assert "layoutStats" in layout
        assert "components" in layout
        assert layout["layoutStats"]["componentCount"] > 0

