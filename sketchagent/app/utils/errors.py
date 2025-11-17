"""Error handling utilities"""

from typing import Optional
from .logger import get_logger

logger = get_logger(__name__)


class AgentError(Exception):
    """Base exception for agent errors"""
    def __init__(self, message: str, session_id: Optional[str] = None):
        self.message = message
        self.session_id = session_id
        super().__init__(self.message)


class ValidationError(AgentError):
    """Validation error"""
    pass


class ExecutionError(AgentError):
    """Operation execution error"""
    pass


class LLMError(AgentError):
    """LLM API error"""
    pass


class RedisError(AgentError):
    """Redis operation error"""
    pass

