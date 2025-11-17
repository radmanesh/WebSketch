"""Enhanced debug logging utilities"""

import time
from typing import Any, Optional
from contextlib import contextmanager
from .logger import get_logger

logger = get_logger(__name__)


@contextmanager
def log_node_execution(node_name: str, session_id: Optional[str] = None):
    """Context manager for logging node execution with timing"""
    start_time = time.time()
    logger.debug(
        "Node execution started",
        node=node_name,
        session_id=session_id,
    )
    try:
        yield
    finally:
        elapsed = time.time() - start_time
        logger.debug(
            "Node execution completed",
            node=node_name,
            session_id=session_id,
            duration_seconds=round(elapsed, 3),
        )


def log_state_snapshot(state: dict[str, Any], stage: str, session_id: Optional[str] = None):
    """Log a snapshot of agent state"""
    snapshot = {
        "stage": stage,
        "step": state.get("step"),
        "error": state.get("error"),
        "component_count": len(state.get("current_sketch", [])),
        "has_operations": state.get("operations") is not None,
        "has_modification": state.get("modification") is not None,
        "has_modified_sketch": state.get("modified_sketch") is not None,
        "retry_count": state.get("retry_count", 0),
    }
    logger.debug(
        "State snapshot",
        session_id=session_id,
        **snapshot,
    )
    return snapshot


def log_llm_request(
    system_prompt_length: int,
    user_prompt_length: int,
    session_id: Optional[str] = None,
):
    """Log LLM request (without sensitive data)"""
    logger.debug(
        "LLM request",
        session_id=session_id,
        system_prompt_length=system_prompt_length,
        user_prompt_length=user_prompt_length,
    )


def log_llm_response(
    response_length: int,
    session_id: Optional[str] = None,
    has_json: bool = False,
):
    """Log LLM response (without content)"""
    logger.debug(
        "LLM response received",
        session_id=session_id,
        response_length=response_length,
        has_json=has_json,
    )


def log_graph_transition(
    from_node: str,
    to_node: str,
    session_id: Optional[str] = None,
):
    """Log graph state transition"""
    logger.debug(
        "Graph transition",
        session_id=session_id,
        from_node=from_node,
        to_node=to_node,
    )

