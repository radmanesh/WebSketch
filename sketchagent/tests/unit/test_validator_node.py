"""Tests for validator node"""

import pytest
from tests.fixtures import (
    create_sample_sketch,
    create_move_operation,
    create_resize_operation,
    create_add_operation,
    create_invalid_operation,
)
from tests.helpers import create_agent_state, assert_state_step, assert_state_error
from app.agent.nodes.validator import validate_node


@pytest.mark.unit
class TestValidatorNode:
    """Test validator node functionality"""

    def test_validate_success(self, sample_sketch):
        """Test successful validation"""
        operations = [
            create_move_operation("component-1", 200, 100),
        ]

        state = create_agent_state(
            current_sketch=sample_sketch,
            step="validate",
            operations=operations,
        )

        result = validate_node(state)

        assert_state_step(result, "execute")
        assert_state_error(result, should_have_error=False)

    def test_validate_multiple_operations(self, sample_sketch):
        """Test validation with multiple operations"""
        operations = [
            create_move_operation("component-1", 200, 100),
            create_resize_operation("component-2", 150, 50),
        ]

        state = create_agent_state(
            current_sketch=sample_sketch,
            step="validate",
            operations=operations,
        )

        result = validate_node(state)

        assert_state_step(result, "execute")
        assert_state_error(result, should_have_error=False)

    def test_validate_no_operations(self, sample_sketch):
        """Test validation with no operations"""
        state = create_agent_state(
            current_sketch=sample_sketch,
            step="validate",
            operations=None,
        )

        result = validate_node(state)

        assert_state_step(result, "error")
        assert_state_error(result, should_have_error=True)
        assert "No operations" in result["error"]

    def test_validate_empty_operations_list(self, sample_sketch):
        """Test validation with empty operations list"""
        state = create_agent_state(
            current_sketch=sample_sketch,
            step="validate",
            operations=[],
        )

        result = validate_node(state)

        assert_state_step(result, "error")
        assert_state_error(result, should_have_error=True)

    def test_validate_missing_component_id(self, sample_sketch):
        """Test validation with missing component ID"""
        operations = [
            create_move_operation(None, 200, 100),  # type: ignore
        ]

        state = create_agent_state(
            current_sketch=sample_sketch,
            step="validate",
            operations=operations,
        )

        result = validate_node(state)

        assert_state_step(result, "error")
        assert_state_error(result, should_have_error=True)

    def test_validate_nonexistent_component(self, sample_sketch):
        """Test validation with non-existent component ID"""
        operations = [
            create_move_operation("nonexistent-id", 200, 100),
        ]

        state = create_agent_state(
            current_sketch=sample_sketch,
            step="validate",
            operations=operations,
        )

        result = validate_node(state)

        assert_state_step(result, "error")
        assert_state_error(result, should_have_error=True)
        assert "not found" in result["error"].lower()

    def test_validate_invalid_resize(self, sample_sketch):
        """Test validation with invalid resize (too small)"""
        operations = [
            create_resize_operation("component-1", 10, 10),  # Too small
        ]

        state = create_agent_state(
            current_sketch=sample_sketch,
            step="validate",
            operations=operations,
        )

        result = validate_node(state)

        assert_state_step(result, "error")
        assert_state_error(result, should_have_error=True)

    def test_validate_add_operation(self, sample_sketch):
        """Test validation of add operation"""
        operations = [
            create_add_operation("Button", 500, 500, 100, 50),
        ]

        state = create_agent_state(
            current_sketch=sample_sketch,
            step="validate",
            operations=operations,
        )

        result = validate_node(state)

        assert_state_step(result, "execute")
        assert_state_error(result, should_have_error=False)

    def test_validate_no_current_sketch(self):
        """Test validation when current_sketch is None"""
        from tests.fixtures import create_move_operation

        operations = [create_move_operation("component-1", 200, 100)]

        # Create state with explicit None for current_sketch
        state: dict = {
            "session_id": "test-session",
            "user_message": "Test",
            "current_sketch": None,  # type: ignore
            "message_history": None,
            "layout_analysis": None,
            "operations": operations,
            "modification": None,
            "modified_sketch": None,
            "step": "validate",
            "error": None,
            "initial_sketch": [],
            "latest_sketch": [],
            "retry_count": 0,
        }

        result = validate_node(state)

        assert_state_step(result, "error")
        assert_state_error(result, should_have_error=True)
        assert "current sketch" in result["error"].lower()

