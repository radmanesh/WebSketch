"""Tests for analyzer node"""

import pytest
from tests.fixtures import create_sample_sketch, create_empty_sketch
from tests.helpers import create_agent_state, assert_state_step, assert_state_error
from app.agent.nodes.analyzer import analyze_node


@pytest.mark.unit
class TestAnalyzerNode:
    """Test analyzer node functionality"""

    def test_analyze_success(self, sample_sketch):
        """Test successful analysis"""
        state = create_agent_state(
            current_sketch=sample_sketch,
            step="analyze",
        )

        result = analyze_node(state)

        assert_state_step(result, "modify")
        assert_state_error(result, should_have_error=False)
        assert result["layout_analysis"] is not None
        assert "layoutStats" in result["layout_analysis"]
        assert result["layout_analysis"]["layoutStats"]["componentCount"] == len(sample_sketch)

    def test_analyze_empty_sketch(self, empty_sketch):
        """Test analysis with empty sketch"""
        state = create_agent_state(
            current_sketch=empty_sketch,
            step="analyze",
        )

        result = analyze_node(state)

        assert_state_step(result, "modify")
        assert_state_error(result, should_have_error=False)
        assert result["layout_analysis"] is not None
        assert result["layout_analysis"]["layoutStats"]["componentCount"] == 0

    def test_analyze_single_component(self):
        """Test analysis with single component"""
        from tests.fixtures import create_single_component_sketch

        sketch = create_single_component_sketch()
        state = create_agent_state(
            current_sketch=sketch,
            step="analyze",
        )

        result = analyze_node(state)

        assert_state_step(result, "modify")
        assert_state_error(result, should_have_error=False)
        assert result["layout_analysis"] is not None
        assert result["layout_analysis"]["layoutStats"]["componentCount"] == 1

    def test_analyze_preserves_session_id(self, sample_sketch):
        """Test that analysis preserves session ID"""
        session_id = "test-session-123"
        state = create_agent_state(
            session_id=session_id,
            current_sketch=sample_sketch,
            step="analyze",
        )

        result = analyze_node(state)

        assert result["session_id"] == session_id

