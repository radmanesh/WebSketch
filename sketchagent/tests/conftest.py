"""Pytest configuration and fixtures"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from typing import AsyncGenerator
from app.services.llm_service import LLMService
from app.services.redis_service import RedisService
from app.schemas.sketch import PlacedComponent
from tests.fixtures import create_sample_sketch, create_empty_sketch, create_single_component_sketch


@pytest.fixture
def sample_sketch() -> list[PlacedComponent]:
    """Sample sketch fixture"""
    return create_sample_sketch()


@pytest.fixture
def empty_sketch() -> list[PlacedComponent]:
    """Empty sketch fixture"""
    return create_empty_sketch()


@pytest.fixture
def single_component_sketch() -> list[PlacedComponent]:
    """Single component sketch fixture"""
    return create_single_component_sketch()


@pytest.fixture
def mock_llm_service() -> LLMService:
    """Mock LLM service that returns configurable responses"""
    service = MagicMock(spec=LLMService)
    service.invoke = AsyncMock(return_value='{"operations": [], "reasoning": "Test", "description": "Test"}')
    return service


@pytest.fixture
def mock_llm_service_with_response() -> callable:
    """Factory for mock LLM service with custom response"""
    def _create_mock(response: str):
        service = MagicMock(spec=LLMService)
        service.invoke = AsyncMock(return_value=response)
        return service
    return _create_mock


@pytest.fixture
async def mock_redis_service() -> AsyncGenerator[RedisService, None]:
    """Mock Redis service using in-memory storage"""
    service = MagicMock(spec=RedisService)

    # In-memory storage
    storage: dict[str, dict] = {}

    async def create_session(initial_sketch: list[PlacedComponent], session_id: str = None):
        import uuid
        from datetime import datetime, UTC
        if not session_id:
            session_id = str(uuid.uuid4())
        storage[session_id] = {
            "session_id": session_id,
            "created_at": datetime.now(UTC).isoformat(),
            "updated_at": datetime.now(UTC).isoformat(),
            "initial_sketch": [comp.model_dump() for comp in initial_sketch],
            "latest_sketch": [comp.model_dump() for comp in initial_sketch],
            "current_sketch": [comp.model_dump() for comp in initial_sketch],
            "operation_history": [],
            "message_history": [],
        }
        return session_id

    async def get_session(session_id: str):
        return storage.get(session_id)

    async def update_session(session_id: str, **kwargs):
        if session_id in storage:
            from datetime import datetime, UTC
            storage[session_id]["updated_at"] = datetime.now(UTC).isoformat()
            for key, value in kwargs.items():
                if key == "current_sketch" and value:
                    storage[session_id]["current_sketch"] = [
                        comp.model_dump() if hasattr(comp, "model_dump") else comp
                        for comp in value
                    ]
                elif key == "operations" and value:
                    storage[session_id]["operation_history"] = [
                        op.model_dump() if hasattr(op, "model_dump") else op
                        for op in value
                    ]

    async def delete_session(session_id: str):
        if session_id in storage:
            del storage[session_id]

    async def get_latest_sketch(session_id: str):
        session = storage.get(session_id)
        if session and session.get("latest_sketch"):
            return [
                PlacedComponent(**comp) for comp in session["latest_sketch"]
            ]
        return None

    async def extend_session_ttl(session_id: str):
        pass  # No-op for mock

    service.create_session = AsyncMock(side_effect=create_session)
    service.get_session = AsyncMock(side_effect=get_session)
    service.update_session = AsyncMock(side_effect=update_session)
    service.delete_session = AsyncMock(side_effect=delete_session)
    service.get_latest_sketch = AsyncMock(side_effect=get_latest_sketch)
    service.extend_session_ttl = AsyncMock(side_effect=extend_session_ttl)

    yield service


@pytest.fixture
def agent_state(sample_sketch):
    """Agent state fixture"""
    from tests.helpers import create_agent_state
    return create_agent_state(current_sketch=sample_sketch)

