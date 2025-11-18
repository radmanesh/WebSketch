"""LangGraph state machine for multi-agent workflow"""

from typing import Literal
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from .state import AgentState
from .nodes.analyzer import analyze_node
from .nodes.modifier import modify_node
from .nodes.validator import validate_node
from .nodes.executor import execute_node
from .nodes.image_analyzer import image_analyzer_node
from ..services.llm_service import LLMService
from ..services.image_analysis_service import ImageAnalysisService
from ..utils.logger import get_logger

logger = get_logger(__name__)


def should_continue_after_analyze(state: AgentState) -> Literal["modify", "end"]:
    """Determine next step after analyze node"""
    if isinstance(state, dict):
        step = state.get("step", "analyze")
    else:
        step = getattr(state, "step", "analyze")

    if step == "error":
        return "end"
    return "modify"


def should_continue_after_modify(state: AgentState) -> Literal["validate", "end"]:
    """Determine next step after modify node"""
    if isinstance(state, dict):
        step = state.get("step", "modify")
    else:
        step = getattr(state, "step", "modify")

    if step == "error":
        return "end"
    if step == "complete":
        return "end"
    return "validate"


def should_continue_after_validate(state: AgentState) -> Literal["execute", "end"]:
    """Determine next step after validate node"""
    if isinstance(state, dict):
        step = state.get("step", "validate")
    else:
        step = getattr(state, "step", "validate")

    if step == "error":
        return "end"
    return "execute"


def should_continue_after_execute(state: AgentState) -> Literal["end"]:
    """Determine next step after execute node"""
    return "end"


def should_continue_after_image_analyze(state: AgentState) -> Literal["analyze", "end"]:
    """Determine next step after image analyze node"""
    if isinstance(state, dict):
        step = state.get("step", "image_analyze")
    else:
        step = getattr(state, "step", "image_analyze")

    if step == "error":
        return "end"
    if step == "complete":
        return "end"
    return "analyze"


def route_from_start(state: AgentState) -> Literal["image_analyze", "analyze"]:
    """Route from start based on whether image data exists"""
    if isinstance(state, dict):
        image_data = state.get("image_data")
    else:
        image_data = getattr(state, "image_data", None)

    if image_data:
        return "image_analyze"
    return "analyze"


def create_agent_graph(llm_service: LLMService) -> StateGraph:
    """Create LangGraph state machine"""
    # Create image analysis service
    image_analysis_service = ImageAnalysisService(llm_service)

    # Create graph
    workflow = StateGraph(AgentState)

    # Add nodes
    # Image analyzer node (runs first if image is present)
    async def image_analyzer_wrapper(state: AgentState):
        return await image_analyzer_node(state, image_analysis_service)

    workflow.add_node("image_analyze", image_analyzer_wrapper)
    workflow.add_node("analyze", analyze_node)

    # Create async wrapper for modify node
    async def modify_wrapper(state: AgentState):
        return await modify_node(state, llm_service)

    workflow.add_node("modify", modify_wrapper)
    workflow.add_node("validate", validate_node)
    workflow.add_node("execute", execute_node)

    # Set entry point and add conditional routing
    workflow.set_entry_point("start")

    # Add start node that routes based on image data
    def start_node(state: AgentState) -> AgentState:
        """Start node that routes to image_analyze or analyze"""
        return state

    workflow.add_node("start", start_node)

    workflow.add_conditional_edges(
        "start",
        route_from_start,
        {
            "image_analyze": "image_analyze",
            "analyze": "analyze",
        },
    )

    # Add conditional edges with node-specific routing functions
    workflow.add_conditional_edges(
        "image_analyze",
        should_continue_after_image_analyze,
        {
            "analyze": "analyze",
            "end": END,
        },
    )

    workflow.add_conditional_edges(
        "analyze",
        should_continue_after_analyze,
        {
            "modify": "modify",
            "end": END,
        },
    )

    workflow.add_conditional_edges(
        "modify",
        should_continue_after_modify,
        {
            "validate": "validate",
            "end": END,
        },
    )

    workflow.add_conditional_edges(
        "validate",
        should_continue_after_validate,
        {
            "execute": "execute",
            "end": END,
        },
    )

    workflow.add_conditional_edges(
        "execute",
        should_continue_after_execute,
        {
            "end": END,
        },
    )

    # Compile graph
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)

    return app

