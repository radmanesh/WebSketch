"""Validator agent node - validates operations before execution"""

from ..state import AgentState
from ...tools.operation_executor import validate_operations
from ...utils.logger import get_logger
from ...utils.errors import ValidationError

logger = get_logger(__name__)


def validate_node(state: AgentState) -> AgentState:
    """Validate operations before execution"""
    logger.info("Validating operations", session_id=state["session_id"])

    if not state.get("operations"):
        state["step"] = "error"
        state["error"] = "No operations to validate"
        return state

    try:
        is_valid, error_msg = validate_operations(
            state["current_sketch"], state["operations"]
        )

        if not is_valid:
            raise ValidationError(f"Validation failed: {error_msg}")

        state["step"] = "execute"
        logger.info("Operations validated", session_id=state["session_id"])
    except ValidationError as e:
        logger.error("Validation failed", error=str(e), session_id=state["session_id"])
        state["step"] = "error"
        state["error"] = str(e)
    except Exception as e:
        logger.error("Validation error", error=str(e), session_id=state["session_id"])
        state["step"] = "error"
        state["error"] = f"Validation error: {str(e)}"

    return state

