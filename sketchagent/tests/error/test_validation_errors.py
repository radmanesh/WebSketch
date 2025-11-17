"""Tests for validation error handling"""

import pytest
from tests.fixtures import create_sample_sketch, create_move_operation
from tests.helpers import create_agent_state, assert_state_error
from app.agent.nodes.validator import validate_node
from app.utils.errors import ValidationError


@pytest.mark.error
class TestValidationErrors:
    """Test validation error scenarios"""

    def test_validate_missing_component_id(self, sample_sketch):
        """Test validation error when component ID is missing"""
        operations = [
            create_move_operation(None, 200, 100),  # type: ignore
        ]

        state = create_agent_state(
            current_sketch=sample_sketch,
            step="validate",
            operations=operations,
        )

        result = validate_node(state)

        assert_state_error(result, should_have_error=True)
        assert "componentId" in result["error"].lower() or "missing" in result["error"].lower()

    def test_validate_invalid_component_id(self, sample_sketch):
        """Test validation error when component doesn't exist"""
        operations = [
            create_move_operation("invalid-id-123", 200, 100),
        ]

        state = create_agent_state(
            current_sketch=sample_sketch,
            step="validate",
            operations=operations,
        )

        result = validate_node(state)

        assert_state_error(result, should_have_error=True)
        assert "not found" in result["error"].lower()

    def test_validate_invalid_resize_dimensions(self, sample_sketch):
        """Test validation error for invalid resize dimensions"""
        from tests.fixtures import create_resize_operation

        operations = [
            create_resize_operation("component-1", 10, 10),  # Too small
        ]

        state = create_agent_state(
            current_sketch=sample_sketch,
            step="validate",
            operations=operations,
        )

        result = validate_node(state)

        assert_state_error(result, should_have_error=True)

    def test_validate_missing_coordinates(self, sample_sketch):
        """Test validation error when coordinates are missing"""
        from tests.fixtures import create_move_operation
        from app.schemas.sketch import ComponentOperation

        operations = [
            ComponentOperation(
                type="move",
                componentId="component-1",
                x=None,  # Missing
                y=None,  # Missing
            ),
        ]

        state = create_agent_state(
            current_sketch=sample_sketch,
            step="validate",
            operations=operations,
        )

        result = validate_node(state)

        assert_state_error(result, should_have_error=True)

    def test_validate_empty_operations(self, sample_sketch):
        """Test validation error with empty operations"""
        state = create_agent_state(
            current_sketch=sample_sketch,
            step="validate",
            operations=[],
        )

        result = validate_node(state)

        assert_state_error(result, should_have_error=True)

    def test_validate_no_current_sketch(self):
        """Test validation error when current sketch is None"""
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

        assert_state_error(result, should_have_error=True)
        assert "current sketch" in result["error"].lower()

