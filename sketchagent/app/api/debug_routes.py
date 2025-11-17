"""Debug API routes for development and testing"""

import json
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from ..schemas.sketch import PlacedComponent
from ..services.redis_service import RedisService
from ..services.llm_service import LLMService
from ..agent.graph import create_agent_graph
from ..agent.state import AgentState
from ..utils.logger import get_logger
from .dependencies import verify_api_key
from ..config import settings

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/debug", tags=["debug"])

# Services will be injected via dependency injection
_debug_redis_service: Optional[RedisService] = None
_debug_llm_service: Optional[LLMService] = None


def set_debug_services(redis: RedisService, llm: LLMService) -> None:
    """Set the service instances (called from main.py)"""
    global _debug_redis_service, _debug_llm_service
    _debug_redis_service = redis
    _debug_llm_service = llm


def get_debug_redis_service() -> RedisService:
    """Dependency to get Redis service"""
    if _debug_redis_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Redis service not initialized",
        )
    return _debug_redis_service


def get_debug_llm_service() -> LLMService:
    """Dependency to get LLM service"""
    if _debug_llm_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM service not initialized",
        )
    return _debug_llm_service


def check_debug_enabled():
    """Check if debug mode is enabled"""
    # Only enable in development (when log level is DEBUG or DEBUG_MODE env var is set)
    if settings.log_level.upper() != "DEBUG":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Debug endpoints are only available in DEBUG mode",
        )


@router.get("/state/{session_id}")
async def get_agent_state(
    session_id: str,
    redis: RedisService = Depends(get_debug_redis_service),
    _: str = Depends(verify_api_key),
):
    """Get current agent state for a session"""
    check_debug_enabled()

    try:
        session_data = await redis.get_session(session_id)
        if not session_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found",
            )

        # Return sanitized state information
        return {
            "session_id": session_id,
            "created_at": session_data.get("created_at"),
            "updated_at": session_data.get("updated_at"),
            "current_sketch_count": len(session_data.get("current_sketch", [])),
            "operation_history_count": len(session_data.get("operation_history", [])),
            "current_sketch": session_data.get("current_sketch", []),
            "operation_history": session_data.get("operation_history", []),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get debug state", error=str(e), session_id=session_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get debug state: {str(e)}",
        )


@router.post("/test-node")
async def test_node(
    node_name: str,
    state_data: dict,
    llm: LLMService = Depends(get_debug_llm_service),
    _: str = Depends(verify_api_key),
):
    """Test an individual node in isolation"""
    check_debug_enabled()

    try:
        from ..agent.nodes.analyzer import analyze_node
        from ..agent.nodes.modifier import modify_node
        from ..agent.nodes.validator import validate_node
        from ..agent.nodes.executor import execute_node

        # Convert state data to AgentState
        state: AgentState = {
            "session_id": state_data.get("session_id", "debug-session"),
            "user_message": state_data.get("user_message", ""),
            "current_sketch": [
                PlacedComponent(**comp) if isinstance(comp, dict) else comp
                for comp in state_data.get("current_sketch", [])
            ],
            "message_history": state_data.get("message_history"),
            "layout_analysis": state_data.get("layout_analysis"),
            "operations": state_data.get("operations"),
            "modification": state_data.get("modification"),
            "modified_sketch": state_data.get("modified_sketch"),
            "step": state_data.get("step", "analyze"),
            "error": state_data.get("error"),
            "initial_sketch": [
                PlacedComponent(**comp) if isinstance(comp, dict) else comp
                for comp in state_data.get("initial_sketch", state_data.get("current_sketch", []))
            ],
            "latest_sketch": [
                PlacedComponent(**comp) if isinstance(comp, dict) else comp
                for comp in state_data.get("latest_sketch", state_data.get("current_sketch", []))
            ],
            "retry_count": state_data.get("retry_count", 0),
        }

        # Execute the specified node
        if node_name == "analyze":
            result = analyze_node(state)
        elif node_name == "modify":
            result = await modify_node(state, llm)
        elif node_name == "validate":
            result = validate_node(state)
        elif node_name == "execute":
            result = execute_node(state)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown node: {node_name}. Valid nodes: analyze, modify, validate, execute",
            )

        # Serialize result for response
        return {
            "node": node_name,
            "input_state": {
                "step": state.get("step"),
                "component_count": len(state.get("current_sketch", [])),
                "has_operations": state.get("operations") is not None,
            },
            "output_state": {
                "step": result.get("step"),
                "error": result.get("error"),
                "component_count": len(result.get("current_sketch", [])),
                "has_operations": result.get("operations") is not None,
                "has_modification": result.get("modification") is not None,
                "has_modified_sketch": result.get("modified_sketch") is not None,
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Node test failed", error=str(e), node=node_name, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Node test failed: {str(e)}",
        )


@router.get("/graph/{session_id}")
async def get_graph_history(
    session_id: str,
    redis: RedisService = Depends(get_debug_redis_service),
    _: str = Depends(verify_api_key),
):
    """Get graph execution history for a session"""
    check_debug_enabled()

    try:
        # This would require storing graph execution history
        # For now, return session state as a proxy
        session_data = await redis.get_session(session_id)
        if not session_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found",
            )

        return {
            "session_id": session_id,
            "operation_history": session_data.get("operation_history", []),
            "note": "Full graph execution history requires additional logging infrastructure",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get graph history", error=str(e), session_id=session_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get graph history: {str(e)}",
        )

