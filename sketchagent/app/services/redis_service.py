"""Redis service for session state management"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Optional
import redis.asyncio as redis
from ..schemas.sketch import PlacedComponent
from ..schemas.api import ChatMessage
from ..utils.logger import get_logger
from ..utils.errors import RedisError

logger = get_logger(__name__)

# Redis key prefix
SESSION_PREFIX = "sketchagent:session:"
SESSION_TTL = 3600  # 1 hour in seconds


class RedisService:
    """Redis service for managing session state"""

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.client: Optional[redis.Redis] = None

    async def connect(self) -> None:
        """Connect to Redis"""
        try:
            self.client = await redis.from_url(
                self.redis_url, encoding="utf-8", decode_responses=True
            )
            await self.client.ping()
            logger.info("Connected to Redis", redis_url=self.redis_url)
        except Exception as e:
            logger.error("Failed to connect to Redis", error=str(e))
            raise RedisError(f"Failed to connect to Redis: {str(e)}")

    async def disconnect(self) -> None:
        """Disconnect from Redis"""
        if self.client:
            await self.client.close()
            logger.info("Disconnected from Redis")

    def _session_key(self, session_id: str) -> str:
        """Get Redis key for session"""
        return f"{SESSION_PREFIX}{session_id}"

    async def create_session(
        self,
        initial_sketch: list[PlacedComponent],
        session_id: Optional[str] = None,
    ) -> str:
        """Create a new session"""
        if not session_id:
            session_id = str(uuid.uuid4())

        session_data = {
            "session_id": session_id,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "initial_sketch": [comp.model_dump() for comp in initial_sketch],
            "latest_sketch": [comp.model_dump() for comp in initial_sketch],
            "current_sketch": [comp.model_dump() for comp in initial_sketch],
            "operation_history": [],
            "message_history": [],
        }

        key = self._session_key(session_id)
        try:
            await self.client.setex(
                key, SESSION_TTL, json.dumps(session_data, default=str)
            )
            logger.info("Created session", session_id=session_id)
            return session_id
        except Exception as e:
            logger.error("Failed to create session", error=str(e), session_id=session_id)
            raise RedisError(f"Failed to create session: {str(e)}")

    async def get_session(self, session_id: str) -> Optional[dict]:
        """Get session data"""
        key = self._session_key(session_id)
        try:
            data = await self.client.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error("Failed to get session", error=str(e), session_id=session_id)
            raise RedisError(f"Failed to get session: {str(e)}")

    async def update_session(
        self,
        session_id: str,
        current_sketch: Optional[list[PlacedComponent]] = None,
        operations: Optional[list] = None,
        message: Optional[ChatMessage] = None,
    ) -> None:
        """Update session data"""
        session_data = await self.get_session(session_id)
        if not session_data:
            raise RedisError(f"Session {session_id} not found")

        # Update timestamp
        session_data["updated_at"] = datetime.utcnow().isoformat()

        # Update sketch
        if current_sketch is not None:
            session_data["current_sketch"] = [comp.model_dump() for comp in current_sketch]
            session_data["latest_sketch"] = [comp.model_dump() for comp in current_sketch]

        # Add to operation history (for undo/redo)
        if operations:
            session_data["operation_history"].append({
                "timestamp": datetime.utcnow().isoformat(),
                "operations": [op.model_dump() if hasattr(op, "model_dump") else op for op in operations],
            })

        # Add to message history
        if message:
            session_data["message_history"].append({
                "role": message.role,
                "content": message.content,
                "timestamp": message.timestamp or datetime.utcnow().isoformat(),
            })

        key = self._session_key(session_id)
        try:
            await self.client.setex(
                key, SESSION_TTL, json.dumps(session_data, default=str)
            )
            logger.debug("Updated session", session_id=session_id)
        except Exception as e:
            logger.error("Failed to update session", error=str(e), session_id=session_id)
            raise RedisError(f"Failed to update session: {str(e)}")

    async def get_latest_sketch(self, session_id: str) -> Optional[list[PlacedComponent]]:
        """Get latest sketch from session"""
        session_data = await self.get_session(session_id)
        if not session_data:
            return None

        latest = session_data.get("latest_sketch")
        if latest:
            return [PlacedComponent(**comp) for comp in latest]
        return None

    async def get_initial_sketch(self, session_id: str) -> Optional[list[PlacedComponent]]:
        """Get initial sketch from session"""
        session_data = await self.get_session(session_id)
        if not session_data:
            return None

        initial = session_data.get("initial_sketch")
        if initial:
            return [PlacedComponent(**comp) for comp in initial]
        return None

    async def get_operation_history(self, session_id: str) -> list:
        """Get operation history for undo/redo"""
        session_data = await self.get_session(session_id)
        if not session_data:
            return []

        return session_data.get("operation_history", [])

    async def delete_session(self, session_id: str) -> None:
        """Delete a session"""
        key = self._session_key(session_id)
        try:
            await self.client.delete(key)
            logger.info("Deleted session", session_id=session_id)
        except Exception as e:
            logger.error("Failed to delete session", error=str(e), session_id=session_id)
            raise RedisError(f"Failed to delete session: {str(e)}")

    async def extend_session_ttl(self, session_id: str) -> None:
        """Extend session TTL"""
        key = self._session_key(session_id)
        try:
            await self.client.expire(key, SESSION_TTL)
        except Exception as e:
            logger.error("Failed to extend session TTL", error=str(e), session_id=session_id)

