"""Test helper utilities"""

import json
from typing import Any, Optional
from app.agent.state import AgentState
from app.schemas.sketch import PlacedComponent


def create_agent_state(
    session_id: str = "test-session",
    user_message: str = "Test message",
    current_sketch: Optional[list[PlacedComponent]] = None,
    step: str = "analyze",
    **kwargs,
) -> AgentState:
    """Create a test agent state"""
    if current_sketch is None and "current_sketch" not in kwargs:
        from tests.fixtures import create_sample_sketch

        current_sketch = create_sample_sketch()

    # Allow explicit None to be passed through
    if "current_sketch" in kwargs:
        current_sketch = kwargs.pop("current_sketch")

    state: AgentState = {
        "session_id": session_id,
        "user_message": user_message,
        "current_sketch": current_sketch,  # type: ignore
        "message_history": None,
        "layout_analysis": None,
        "operations": None,
        "modification": None,
        "modified_sketch": None,
        "step": step,
        "error": None,
        "initial_sketch": current_sketch.copy() if current_sketch else [],  # type: ignore
        "latest_sketch": current_sketch.copy() if current_sketch else [],  # type: ignore
        "retry_count": 0,
        **kwargs,
    }
    return state


def assert_state_step(state: AgentState, expected_step: str) -> None:
    """Assert that state step matches expected value"""
    assert state["step"] == expected_step, f"Expected step '{expected_step}', got '{state['step']}'"


def assert_state_error(state: AgentState, should_have_error: bool = True) -> None:
    """Assert error state"""
    if should_have_error:
        assert state["error"] is not None, "Expected error but state.error is None"
        assert state["step"] == "error", f"Expected step 'error', got '{state['step']}'"
    else:
        assert state["error"] is None, f"Unexpected error: {state['error']}"


def assert_sketch_valid(sketch: list[PlacedComponent]) -> None:
    """Assert that sketch components are valid"""
    for comp in sketch:
        assert comp.width >= 20 or comp.type.value == "HorizontalLine", f"Invalid width: {comp.width}"
        assert comp.height >= 2, f"Invalid height: {comp.height}"
        assert comp.x >= 0, f"Invalid x: {comp.x}"
        assert comp.y >= 0, f"Invalid y: {comp.y}"


def serialize_state_for_debug(state: AgentState) -> dict[str, Any]:
    """Serialize agent state for debugging"""
    return {
        "session_id": state.get("session_id"),
        "step": state.get("step"),
        "error": state.get("error"),
        "user_message": state.get("user_message"),
        "component_count": len(state.get("current_sketch", [])),
        "has_operations": state.get("operations") is not None,
        "has_modification": state.get("modification") is not None,
        "has_modified_sketch": state.get("modified_sketch") is not None,
        "retry_count": state.get("retry_count", 0),
    }

