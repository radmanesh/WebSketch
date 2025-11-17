"""Analyzer agent node"""

from ..state import AgentState
from ...tools.sketch_parser import parse_sketch_layout
from ...utils.logger import get_logger

logger = get_logger(__name__)


def analyze_node(state: AgentState) -> AgentState:
    """Analyze the current sketch layout"""
    logger.info("Analyzing sketch layout", session_id=state["session_id"])

    try:
        layout_analysis = parse_sketch_layout(state["current_sketch"])

        state["layout_analysis"] = layout_analysis
        state["step"] = "modify"

        logger.info(
            "Layout analysis complete",
            session_id=state["session_id"],
            component_count=layout_analysis["layoutStats"]["componentCount"],
        )
    except Exception as e:
        logger.error("Analysis failed", error=str(e), session_id=state["session_id"])
        state["step"] = "error"
        state["error"] = f"Analysis failed: {str(e)}"

    return state

