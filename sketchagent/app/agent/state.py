"""LangGraph state definition"""

from typing import TypedDict, Optional, Annotated
from langgraph.graph.message import add_messages
from ..schemas.sketch import PlacedComponent, ComponentOperation, SketchModification
from ..tools.sketch_parser import LayoutAnalysis


class AgentState(TypedDict):
    """Agent state for LangGraph"""
    # Session management
    session_id: str

    # Input
    user_message: str
    current_sketch: list[PlacedComponent]
    message_history: Optional[list[dict]]

    # Analysis step
    layout_analysis: Optional[LayoutAnalysis]

    # Modification step
    operations: Optional[list[ComponentOperation]]
    modification: Optional[SketchModification]

    # Execution step
    modified_sketch: Optional[list[PlacedComponent]]

    # State tracking
    step: str  # "analyze", "modify", "validate", "execute", "complete", "error"
    error: Optional[str]

    # Fallback data
    initial_sketch: list[PlacedComponent]
    latest_sketch: list[PlacedComponent]
    retry_count: int

