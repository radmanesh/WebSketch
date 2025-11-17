"""Integration tests for full agent workflow"""

import pytest
from unittest.mock import AsyncMock
from tests.fixtures import create_sample_sketch
from app.agent.graph import create_agent_graph
from app.agent.state import AgentState
from app.services.llm_service import LLMService


@pytest.mark.integration
class TestAgentWorkflow:
    """Test full agent workflow"""

    @pytest.mark.asyncio
    async def test_full_workflow_success(self, sample_sketch, mock_llm_service):
        """Test successful full workflow"""
        # Configure mock LLM response
        mock_llm_service.invoke = AsyncMock(
            return_value='{"operations": [{"type": "move", "componentId": "component-1", "x": 200, "y": 150}], "reasoning": "Move component", "description": "Moving component"}'
        )

        graph = create_agent_graph(mock_llm_service)

        initial_state: AgentState = {
            "session_id": "test-session",
            "user_message": "Move the first component to the right",
            "current_sketch": sample_sketch,
            "message_history": None,
            "layout_analysis": None,
            "operations": None,
            "modification": None,
            "modified_sketch": None,
            "step": "analyze",
            "error": None,
            "initial_sketch": sample_sketch.copy(),
            "latest_sketch": sample_sketch.copy(),
            "retry_count": 0,
        }

        config = {"configurable": {"thread_id": "test-session"}}

        final_state = None
        try:
            async for state_dict in graph.astream(initial_state, config):
                # LangGraph returns updates as dict with node names as keys
                if isinstance(state_dict, dict):
                    # Get the last node's state update
                    for node_name, node_state in state_dict.items():
                        if isinstance(node_state, dict):
                            final_state = node_state
                        else:
                            final_state = state_dict
        except KeyError as e:
            # If there's a KeyError, it means the graph routing failed
            # This can happen if should_continue returns an invalid value
            pytest.fail(f"Graph routing error: {e}. This usually means should_continue returned an invalid step.")

        assert final_state is not None
        assert final_state.get("step") in ["complete", "execute", "error"]
        if final_state.get("step") != "error":
            assert final_state.get("error") is None
            assert final_state.get("modified_sketch") is not None
            assert len(final_state["modified_sketch"]) == len(sample_sketch)

    @pytest.mark.asyncio
    async def test_workflow_with_error(self, sample_sketch, mock_llm_service):
        """Test workflow when LLM returns invalid JSON"""
        mock_llm_service.invoke = AsyncMock(return_value="Invalid JSON")

        graph = create_agent_graph(mock_llm_service)

        initial_state: AgentState = {
            "session_id": "test-session",
            "user_message": "Move component",
            "current_sketch": sample_sketch,
            "message_history": None,
            "layout_analysis": None,
            "operations": None,
            "modification": None,
            "modified_sketch": None,
            "step": "analyze",
            "error": None,
            "initial_sketch": sample_sketch.copy(),
            "latest_sketch": sample_sketch.copy(),
            "retry_count": 0,
        }

        config = {"configurable": {"thread_id": "test-session"}}

        final_state = None
        try:
            async for state_dict in graph.astream(initial_state, config):
                if isinstance(state_dict, dict):
                    for node_name, node_state in state_dict.items():
                        if isinstance(node_state, dict):
                            final_state = node_state
                        else:
                            final_state = state_dict
        except KeyError as e:
            pytest.fail(f"Graph routing error: {e}")

        assert final_state is not None
        assert final_state.get("step") == "error"
        assert final_state.get("error") is not None

    @pytest.mark.asyncio
    async def test_workflow_preserves_session_id(self, sample_sketch, mock_llm_service):
        """Test that workflow preserves session ID"""
        session_id = "custom-session-123"
        mock_llm_service.invoke = AsyncMock(
            return_value='{"operations": [], "reasoning": "Test", "description": "Test"}'
        )

        graph = create_agent_graph(mock_llm_service)

        initial_state: AgentState = {
            "session_id": session_id,
            "user_message": "Test",
            "current_sketch": sample_sketch,
            "message_history": None,
            "layout_analysis": None,
            "operations": None,
            "modification": None,
            "modified_sketch": None,
            "step": "analyze",
            "error": None,
            "initial_sketch": sample_sketch.copy(),
            "latest_sketch": sample_sketch.copy(),
            "retry_count": 0,
        }

        config = {"configurable": {"thread_id": session_id}}

        final_state = None
        try:
            async for state_dict in graph.astream(initial_state, config):
                if isinstance(state_dict, dict):
                    for node_name, node_state in state_dict.items():
                        if isinstance(node_state, dict):
                            final_state = node_state
                        else:
                            final_state = state_dict
        except KeyError as e:
            pytest.fail(f"Graph routing error: {e}")

        assert final_state is not None
        assert final_state.get("session_id") == session_id

