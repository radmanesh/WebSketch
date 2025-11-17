"""LangGraph state machine for multi-agent workflow"""

from typing import Literal
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from .state import AgentState
from .nodes.analyzer import analyze_node
from .nodes.modifier import modify_node
from .nodes.validator import validate_node
from .nodes.executor import execute_node
from ..services.llm_service import LLMService
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


def create_agent_graph(llm_service: LLMService) -> StateGraph:
    """Create LangGraph state machine"""
    # Create graph
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("analyze", analyze_node)

    # Create async wrapper for modify node
    async def modify_wrapper(state: AgentState):
        return await modify_node(state, llm_service)

    workflow.add_node("modify", modify_wrapper)
    workflow.add_node("validate", validate_node)
    workflow.add_node("execute", execute_node)

    # Set entry point
    workflow.set_entry_point("analyze")

    # Add conditional edges with node-specific routing functions
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

