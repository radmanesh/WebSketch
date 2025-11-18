"""Image analyzer agent node"""

from ..state import AgentState
from ...services.image_analysis_service import ImageAnalysisService
from ...utils.logger import get_logger
from ...utils.debug_logger import log_node_execution, log_state_snapshot

logger = get_logger(__name__)


async def image_analyzer_node(
    state: AgentState, image_analysis_service: ImageAnalysisService
) -> AgentState:
    """Analyze image and generate initial wireframe components"""
    session_id = state.get("session_id")
    logger.info("Analyzing image to generate wireframe", session_id=session_id)

    with log_node_execution("image_analyze", session_id):
        log_state_snapshot(state, "before_image_analyze", session_id)
        try:
            image_data = state.get("image_data")
            image_format = state.get("image_format", "bytes")

            if not image_data:
                logger.warning("No image data provided, skipping image analysis", session_id=session_id)
                state["step"] = "analyze"
                return state

            # Analyze image and generate components
            components = await image_analysis_service.analyze_image(
                image_data, image_format, session_id
            )

            # Set generated components as current sketch
            state["current_sketch"] = components
            state["latest_sketch"] = components
            state["initial_sketch"] = components

            # Clear image data from state (no longer needed)
            state["image_data"] = None
            state["image_format"] = None

            # Move to analyze step (or skip if no user message)
            user_message = state.get("user_message", "").strip()
            if user_message:
                # User provided a message, continue with normal workflow
                state["step"] = "analyze"
            else:
                # No message, just return the generated wireframe
                state["step"] = "complete"
                state["modified_sketch"] = components

            logger.info(
                "Image analysis complete",
                session_id=session_id,
                component_count=len(components),
            )
            log_state_snapshot(state, "after_image_analyze", session_id)
        except Exception as e:
            logger.error(
                "Image analysis failed", error=str(e), session_id=session_id, exc_info=True
            )
            state["step"] = "error"
            state["error"] = f"Image analysis failed: {str(e)}"
            log_state_snapshot(state, "image_analyze_error", session_id)

    return state

