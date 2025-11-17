"""Integration tests for API endpoints"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
from app.main import app
from app.api.routes import set_services
from app.services.llm_service import LLMService
from app.services.redis_service import RedisService


@pytest.fixture
def test_client(mock_llm_service, mock_redis_service):
    """Create test client with mocked services"""
    set_services(mock_redis_service, mock_llm_service)
    return TestClient(app)


@pytest.mark.integration
class TestAPIEndpoints:
    """Test API endpoints"""

    def test_health_check(self, test_client):
        """Test health check endpoint"""
        response = test_client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_create_session(self, test_client, sample_sketch):
        """Test session creation"""
        response = test_client.post(
            "/api/v1/session",
            json=[comp.model_dump() for comp in sample_sketch],
            headers={"X-API-Key": "test-key"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "sessionId" in data
        assert "createdAt" in data

    @pytest.mark.asyncio
    async def test_get_session(self, test_client, sample_sketch, mock_redis_service):
        """Test getting session"""
        # First create a session
        session_id = "test-session-123"
        await mock_redis_service.create_session(sample_sketch, session_id)

        response = test_client.get(
            f"/api/v1/session/{session_id}",
            headers={"X-API-Key": "test-key"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["sessionId"] == session_id
        assert "currentSketch" in data

    def test_chat_endpoint(self, test_client, sample_sketch, mock_llm_service):
        """Test chat endpoint"""
        mock_llm_service.invoke = AsyncMock(
            return_value='{"operations": [{"type": "move", "componentId": "component-1", "x": 200, "y": 150}], "reasoning": "Test", "description": "Test"}'
        )

        response = test_client.post(
            "/api/v1/chat",
            json={
                "message": "Move component",
                "currentSketch": [comp.model_dump() for comp in sample_sketch],
            },
            headers={"X-API-Key": "test-key"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "modifiedSketch" in data
        assert "operations" in data

    def test_chat_endpoint_error_handling(self, test_client, sample_sketch, mock_llm_service):
        """Test chat endpoint error handling"""
        mock_llm_service.invoke = AsyncMock(side_effect=Exception("LLM error"))

        response = test_client.post(
            "/api/v1/chat",
            json={
                "message": "Move component",
                "currentSketch": [comp.model_dump() for comp in sample_sketch],
            },
            headers={"X-API-Key": "test-key"},
        )
        assert response.status_code == 200  # Returns ChatResponse with success=False
        data = response.json()
        assert data["success"] is False
        assert "Error" in data.get("reasoning", "") or "Error" in data.get("description", "")

