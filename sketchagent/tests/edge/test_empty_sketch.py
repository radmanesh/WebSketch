"""Tests for edge cases with empty sketch"""

import pytest
from tests.fixtures import create_empty_sketch, create_add_operation
from tests.helpers import create_agent_state, assert_state_step
from app.agent.nodes.analyzer import analyze_node
from app.agent.nodes.executor import execute_node


@pytest.mark.edge
class TestEmptySketch:
    """Test edge cases with empty sketch"""

    def test_analyze_empty_sketch(self, empty_sketch):
        """Test analysis of empty sketch"""
        state = create_agent_state(
            current_sketch=empty_sketch,
            step="analyze",
        )

        result = analyze_node(state)

        assert_state_step(result, "modify")
        assert result["layout_analysis"] is not None
        assert result["layout_analysis"]["layoutStats"]["componentCount"] == 0

    def test_execute_add_to_empty_sketch(self, empty_sketch):
        """Test adding component to empty sketch"""
        operations = [
            create_add_operation("Button", 100, 100, 150, 50),
        ]

        state = create_agent_state(
            current_sketch=empty_sketch,
            step="execute",
            operations=operations,
        )

        result = execute_node(state)

        assert_state_step(result, "complete")
        assert result["modified_sketch"] is not None
        assert len(result["modified_sketch"]) == 1

    def test_execute_delete_from_empty_sketch(self, empty_sketch):
        """Test delete operation on empty sketch"""
        from tests.fixtures import create_delete_operation
        from tests.helpers import assert_state_error

        operations = [
            create_delete_operation("component-1"),
        ]

        state = create_agent_state(
            current_sketch=empty_sketch,
            step="execute",
            operations=operations,
        )

        result = execute_node(state)

        # Should error because component doesn't exist (validation happens in executor)
        assert_state_error(result, should_have_error=True)

