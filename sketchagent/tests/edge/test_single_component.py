"""Tests for edge cases with single component"""

import pytest
from tests.fixtures import create_single_component_sketch, create_move_operation, create_resize_operation
from tests.helpers import create_agent_state, assert_state_step
from app.agent.nodes.analyzer import analyze_node
from app.agent.nodes.executor import execute_node


@pytest.mark.edge
class TestSingleComponent:
    """Test edge cases with single component"""

    def test_analyze_single_component(self):
        """Test analysis of single component sketch"""
        from tests.fixtures import create_single_component_sketch

        sketch = create_single_component_sketch()
        state = create_agent_state(
            current_sketch=sketch,
            step="analyze",
        )

        result = analyze_node(state)

        assert_state_step(result, "modify")
        assert result["layout_analysis"]["layoutStats"]["componentCount"] == 1

    def test_move_single_component(self):
        """Test moving single component"""
        from tests.fixtures import create_single_component_sketch

        sketch = create_single_component_sketch()
        operations = [
            create_move_operation("component-1", 300, 200),
        ]

        state = create_agent_state(
            current_sketch=sketch,
            step="execute",
            operations=operations,
        )

        result = execute_node(state)

        assert_state_step(result, "complete")
        assert len(result["modified_sketch"]) == 1
        assert result["modified_sketch"][0].x == 300
        assert result["modified_sketch"][0].y == 200

    def test_resize_single_component(self):
        """Test resizing single component"""
        from tests.fixtures import create_single_component_sketch

        sketch = create_single_component_sketch()
        operations = [
            create_resize_operation("component-1", 300, 250),
        ]

        state = create_agent_state(
            current_sketch=sketch,
            step="execute",
            operations=operations,
        )

        result = execute_node(state)

        assert_state_step(result, "complete")
        assert result["modified_sketch"][0].width == 300
        assert result["modified_sketch"][0].height == 250

