"""Analyzer agent node"""

from ..state import AgentState
from ...tools.sketch_parser import parse_sketch_layout
from ...utils.logger import get_logger
from ...utils.debug_logger import log_node_execution, log_state_snapshot

logger = get_logger(__name__)


def analyze_node(state: AgentState) -> AgentState:
    """Analyze the current sketch layout"""
    session_id = state.get("session_id")
    logger.info("Analyzing sketch layout", session_id=session_id)

    with log_node_execution("analyze", session_id):
        log_state_snapshot(state, "before_analyze", session_id)
        try:
            layout_analysis = parse_sketch_layout(state["current_sketch"])

            state["layout_analysis"] = layout_analysis
            state["step"] = "modify"

            logger.info(
                "Layout analysis complete",
                session_id=session_id,
                component_count=layout_analysis["layoutStats"]["componentCount"],
            )
            log_state_snapshot(state, "after_analyze", session_id)
        except Exception as e:
            logger.error("Analysis failed", error=str(e), session_id=session_id, exc_info=True)
            state["step"] = "error"
            state["error"] = f"Analysis failed: {str(e)}"
            log_state_snapshot(state, "analyze_error", session_id)

    return state

