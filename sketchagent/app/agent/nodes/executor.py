"""Executor agent node - executes operations and validates result"""

from ..state import AgentState
from ...tools.operation_executor import execute_operations, validate_operations
from ...utils.logger import get_logger
from ...utils.errors import ExecutionError

logger = get_logger(__name__)


def execute_node(state: AgentState) -> AgentState:
    """Execute operations and validate result"""
    logger.info("Executing operations", session_id=state["session_id"])

    if not state.get("operations"):
        state["step"] = "error"
        state["error"] = "No operations to execute"
        return state

    try:
        # Execute operations
        modified_sketch = execute_operations(state["current_sketch"], state["operations"])

        # Validate the result (post-execution validation)
        # Check that all components are valid
        for comp in modified_sketch:
            if comp.width < 20 and comp.type.value != "HorizontalLine":
                raise ExecutionError(f"Component {comp.id} has invalid width: {comp.width}")
            if comp.height < 2:
                raise ExecutionError(f"Component {comp.id} has invalid height: {comp.height}")
            if comp.type.value == "HorizontalLine" and comp.height < 2:
                raise ExecutionError(f"HorizontalLine {comp.id} has invalid height: {comp.height}")

        state["modified_sketch"] = modified_sketch
        state["latest_sketch"] = modified_sketch
        state["step"] = "complete"

        logger.info(
            "Operations executed successfully",
            session_id=state["session_id"],
            component_count=len(modified_sketch),
        )
    except ExecutionError as e:
        logger.error("Execution failed", error=str(e), session_id=state["session_id"])
        state["step"] = "error"
        state["error"] = str(e)
        # Fallback to latest sketch
        state["modified_sketch"] = state.get("latest_sketch") or state["initial_sketch"]
    except Exception as e:
        logger.error("Execution error", error=str(e), session_id=state["session_id"])
        state["step"] = "error"
        state["error"] = f"Execution error: {str(e)}"
        # Fallback to latest sketch
        state["modified_sketch"] = state.get("latest_sketch") or state["initial_sketch"]

    return state

