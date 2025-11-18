"""Validator agent node - validates operations before execution"""

from ..state import AgentState
from ...tools.operation_executor import validate_operations
from ...utils.logger import get_logger
from ...utils.errors import ValidationError

logger = get_logger(__name__)


def validate_node(state: AgentState) -> AgentState:
    """Validate operations before execution"""
    session_id = state.get("session_id", "unknown")
    logger.info("Validating operations", session_id=session_id)

    if not state.get("operations"):
        # Check if step is already complete (no operations needed)
        current_step = state.get("step", "validate")
        if current_step == "complete":
            logger.info(
                "No operations to validate, but step is already complete - passing through",
                session_id=session_id,
            )
            # Keep step as complete and return
            return state

        # Otherwise, this is an error condition
        logger.warning("No operations to validate", session_id=session_id)
        state["step"] = "error"
        state["error"] = "No operations to validate"
        return state

    current_sketch = state.get("current_sketch")
    if not current_sketch:
        logger.error("No current sketch available for validation", session_id=session_id)
        state["step"] = "error"
        state["error"] = "No current sketch available for validation"
        return state

    try:
        is_valid, error_msg = validate_operations(
            current_sketch, state["operations"]
        )

        if not is_valid:
            error_text = f"Validation failed: {error_msg}"
            logger.error("Validation failed", error=error_text, session_id=session_id)
            raise ValidationError(error_text)

        state["step"] = "execute"
        logger.info("Operations validated", session_id=session_id)
    except ValidationError as e:
        logger.error("Validation failed", error=str(e), session_id=session_id)
        state["step"] = "error"
        state["error"] = str(e)
    except Exception as e:
        error_text = f"Validation error: {str(e)}"
        logger.error("Validation error", error=error_text, session_id=session_id, exc_info=True)
        state["step"] = "error"
        state["error"] = error_text

    return state

