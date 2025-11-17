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


def should_continue(state: AgentState) -> Literal["modify", "validate", "execute", "end"]:
    """Determine next step based on current state"""
    step = state.get("step", "analyze")

    if step == "error":
        return "end"
    elif step == "analyze":
        return "modify"
    elif step == "modify":
        return "validate"
    elif step == "validate":
        return "execute"
    elif step == "execute":
        return "end"
    else:
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

    # Add conditional edges
    workflow.add_conditional_edges(
        "analyze",
        should_continue,
        {
            "modify": "modify",
            "end": END,
        },
    )

    workflow.add_conditional_edges(
        "modify",
        should_continue,
        {
            "validate": "validate",
            "end": END,
        },
    )

    workflow.add_conditional_edges(
        "validate",
        should_continue,
        {
            "execute": "execute",
            "end": END,
        },
    )

    workflow.add_conditional_edges(
        "execute",
        should_continue,
        {
            "end": END,
        },
    )

    # Compile graph
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)

    return app

