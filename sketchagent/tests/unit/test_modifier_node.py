"""Tests for modifier node"""

import pytest
from unittest.mock import AsyncMock
from tests.fixtures import create_sample_sketch
from tests.helpers import create_agent_state, assert_state_step, assert_state_error
from app.agent.nodes.modifier import modify_node
from app.services.llm_service import LLMService


@pytest.mark.unit
class TestModifierNode:
    """Test modifier node functionality"""

    @pytest.mark.asyncio
    async def test_modify_success(self, sample_sketch):
        """Test successful modification"""
        mock_llm = AsyncMock(spec=LLMService)
        mock_llm.invoke = AsyncMock(
            return_value='{"operations": [{"type": "move", "componentId": "component-1", "x": 200, "y": 150}], "reasoning": "Move component", "description": "Moving component"}'
        )

        state = create_agent_state(
            current_sketch=sample_sketch,
            step="modify",
            layout_analysis={"description": "Test layout", "layoutStats": {"componentCount": 3}},
        )

        result = await modify_node(state, mock_llm)

        assert_state_step(result, "validate")
        assert_state_error(result, should_have_error=False)
        assert result["operations"] is not None
        assert len(result["operations"]) == 1
        assert result["modification"] is not None
        assert result["modification"].reasoning == "Move component"

    @pytest.mark.asyncio
    async def test_modify_with_json_code_block(self, sample_sketch):
        """Test modification when LLM returns JSON in code block"""
        mock_llm = AsyncMock(spec=LLMService)
        mock_llm.invoke = AsyncMock(
            return_value='```json\n{"operations": [{"type": "move", "componentId": "component-1", "x": 200, "y": 150}], "reasoning": "Test", "description": "Test"}\n```'
        )

        state = create_agent_state(
            current_sketch=sample_sketch,
            step="modify",
            layout_analysis={"description": "Test layout", "layoutStats": {"componentCount": 3}},
        )

        result = await modify_node(state, mock_llm)

        assert_state_step(result, "validate")
        assert_state_error(result, should_have_error=False)
        assert result["operations"] is not None

    @pytest.mark.asyncio
    async def test_modify_invalid_json(self, sample_sketch):
        """Test modification with invalid JSON response"""
        mock_llm = AsyncMock(spec=LLMService)
        mock_llm.invoke = AsyncMock(return_value="Invalid JSON response")

        state = create_agent_state(
            current_sketch=sample_sketch,
            step="modify",
            layout_analysis={"description": "Test layout", "layoutStats": {"componentCount": 3}},
        )

        result = await modify_node(state, mock_llm)

        assert_state_step(result, "error")
        assert_state_error(result, should_have_error=True)
        assert "JSON" in result["error"] or "parse" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_modify_llm_error(self, sample_sketch):
        """Test modification when LLM service fails"""
        mock_llm = AsyncMock(spec=LLMService)
        mock_llm.invoke = AsyncMock(side_effect=Exception("LLM API error"))

        state = create_agent_state(
            current_sketch=sample_sketch,
            step="modify",
            layout_analysis={"description": "Test layout", "layoutStats": {"componentCount": 3}},
        )

        result = await modify_node(state, mock_llm)

        assert_state_step(result, "error")
        assert_state_error(result, should_have_error=True)

    @pytest.mark.asyncio
    async def test_modify_empty_operations(self, sample_sketch):
        """Test modification with empty operations list"""
        mock_llm = AsyncMock(spec=LLMService)
        mock_llm.invoke = AsyncMock(
            return_value='{"operations": [], "reasoning": "No changes needed", "description": "No changes"}'
        )

        state = create_agent_state(
            current_sketch=sample_sketch,
            step="modify",
            layout_analysis={"description": "Test layout", "layoutStats": {"componentCount": 3}},
        )

        result = await modify_node(state, mock_llm)

        assert_state_step(result, "validate")
        assert_state_error(result, should_have_error=False)
        assert result["operations"] is not None
        assert len(result["operations"]) == 0

    @pytest.mark.asyncio
    async def test_modify_multiple_operations(self, sample_sketch):
        """Test modification with multiple operations"""
        mock_llm = AsyncMock(spec=LLMService)
        mock_llm.invoke = AsyncMock(
            return_value='{"operations": [{"type": "move", "componentId": "component-1", "x": 200, "y": 150}, {"type": "resize", "componentId": "component-2", "width": 150, "height": 50}], "reasoning": "Multiple changes", "description": "Multiple changes"}'
        )

        state = create_agent_state(
            current_sketch=sample_sketch,
            step="modify",
            layout_analysis={"description": "Test layout", "layoutStats": {"componentCount": 3}},
        )

        result = await modify_node(state, mock_llm)

        assert_state_step(result, "validate")
        assert_state_error(result, should_have_error=False)
        assert result["operations"] is not None
        assert len(result["operations"]) == 2

