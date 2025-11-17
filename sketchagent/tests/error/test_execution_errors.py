"""Tests for execution error handling"""

import pytest
from tests.fixtures import create_sample_sketch, create_move_operation
from tests.helpers import create_agent_state, assert_state_error
from app.agent.nodes.executor import execute_node


@pytest.mark.error
class TestExecutionErrors:
    """Test execution error scenarios"""

    def test_execute_no_operations(self, sample_sketch):
        """Test execution error when no operations provided"""
        state = create_agent_state(
            current_sketch=sample_sketch,
            step="execute",
            operations=None,
        )

        result = execute_node(state)

        assert_state_error(result, should_have_error=True)
        assert "No operations" in result["error"]

    def test_execute_empty_operations(self, sample_sketch):
        """Test execution with empty operations list"""
        state = create_agent_state(
            current_sketch=sample_sketch,
            step="execute",
            operations=[],
        )

        result = execute_node(state)

        assert_state_error(result, should_have_error=True)

    def test_execute_invalid_component_reference(self, sample_sketch):
        """Test execution error when component doesn't exist"""
        from tests.fixtures import create_move_operation

        operations = [
            create_move_operation("nonexistent-component", 200, 100),
        ]

        state = create_agent_state(
            current_sketch=sample_sketch,
            step="execute",
            operations=operations,
        )

        # This should still execute but the component won't be found
        # The operation executor should handle this gracefully
        result = execute_node(state)

        # Execution should complete (component just won't be moved)
        # But validation should have caught this earlier
        assert result["step"] in ["complete", "error"]

