"""Tests for executor node"""

import pytest
from tests.fixtures import (
    create_sample_sketch,
    create_move_operation,
    create_resize_operation,
    create_add_operation,
    create_delete_operation,
)
from tests.helpers import create_agent_state, assert_state_step, assert_state_error, assert_sketch_valid
from app.agent.nodes.executor import execute_node


@pytest.mark.unit
class TestExecutorNode:
    """Test executor node functionality"""

    def test_execute_move_success(self, sample_sketch):
        """Test successful move operation"""
        operations = [
            create_move_operation("component-1", 200, 150),
        ]

        state = create_agent_state(
            current_sketch=sample_sketch,
            step="execute",
            operations=operations,
        )

        result = execute_node(state)

        assert_state_step(result, "complete")
        assert_state_error(result, should_have_error=False)
        assert result["modified_sketch"] is not None
        assert len(result["modified_sketch"]) == len(sample_sketch)

        # Check that component was moved
        moved_comp = next(
            (c for c in result["modified_sketch"] if c.id == "component-1"), None
        )
        assert moved_comp is not None
        assert moved_comp.x == 200
        assert moved_comp.y == 150

        assert_sketch_valid(result["modified_sketch"])

    def test_execute_resize_success(self, sample_sketch):
        """Test successful resize operation"""
        operations = [
            create_resize_operation("component-1", 400, 60),
        ]

        state = create_agent_state(
            current_sketch=sample_sketch,
            step="execute",
            operations=operations,
        )

        result = execute_node(state)

        assert_state_step(result, "complete")
        assert_state_error(result, should_have_error=False)

        # Check that component was resized
        resized_comp = next(
            (c for c in result["modified_sketch"] if c.id == "component-1"), None
        )
        assert resized_comp is not None
        assert resized_comp.width == 400
        assert resized_comp.height == 60

    def test_execute_add_success(self, sample_sketch):
        """Test successful add operation"""
        operations = [
            create_add_operation("Button", 500, 500, 100, 50),
        ]

        state = create_agent_state(
            current_sketch=sample_sketch,
            step="execute",
            operations=operations,
        )

        result = execute_node(state)

        assert_state_step(result, "complete")
        assert_state_error(result, should_have_error=False)
        assert len(result["modified_sketch"]) == len(sample_sketch) + 1

        # Check that new component was added
        new_components = [
            c for c in result["modified_sketch"] if c.id not in [comp.id for comp in sample_sketch]
        ]
        assert len(new_components) == 1
        assert new_components[0].type.value == "Button"

    def test_execute_delete_success(self, sample_sketch):
        """Test successful delete operation"""
        operations = [
            create_delete_operation("component-1"),
        ]

        state = create_agent_state(
            current_sketch=sample_sketch,
            step="execute",
            operations=operations,
        )

        result = execute_node(state)

        assert_state_step(result, "complete")
        assert_state_error(result, should_have_error=False)
        assert len(result["modified_sketch"]) == len(sample_sketch) - 1

        # Check that component was deleted
        deleted_comp = next(
            (c for c in result["modified_sketch"] if c.id == "component-1"), None
        )
        assert deleted_comp is None

    def test_execute_multiple_operations(self, sample_sketch):
        """Test execution of multiple operations"""
        operations = [
            create_move_operation("component-1", 200, 150),
            create_resize_operation("component-2", 150, 50),
        ]

        state = create_agent_state(
            current_sketch=sample_sketch,
            step="execute",
            operations=operations,
        )

        result = execute_node(state)

        assert_state_step(result, "complete")
        assert_state_error(result, should_have_error=False)
        assert_sketch_valid(result["modified_sketch"])

    def test_execute_no_operations(self, sample_sketch):
        """Test execution with no operations"""
        state = create_agent_state(
            current_sketch=sample_sketch,
            step="execute",
            operations=None,
        )

        result = execute_node(state)

        assert_state_step(result, "error")
        assert_state_error(result, should_have_error=True)
        assert "No operations" in result["error"]

    def test_execute_preserves_other_components(self, sample_sketch):
        """Test that execution preserves components not being modified"""
        operations = [
            create_move_operation("component-1", 200, 150),
        ]

        state = create_agent_state(
            current_sketch=sample_sketch,
            step="execute",
            operations=operations,
        )

        result = execute_node(state)

        # Check that component-2 and component-3 are unchanged
        comp2 = next((c for c in result["modified_sketch"] if c.id == "component-2"), None)
        comp3 = next((c for c in result["modified_sketch"] if c.id == "component-3"), None)

        assert comp2 is not None
        assert comp3 is not None

        # Find original components
        orig_comp2 = next((c for c in sample_sketch if c.id == "component-2"), None)
        orig_comp3 = next((c for c in sample_sketch if c.id == "component-3"), None)

        assert orig_comp2 is not None
        assert orig_comp3 is not None

        assert comp2.x == orig_comp2.x
        assert comp2.y == orig_comp2.y
        assert comp3.x == orig_comp3.x
        assert comp3.y == orig_comp3.y

