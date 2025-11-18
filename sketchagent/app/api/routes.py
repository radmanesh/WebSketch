"""API routes"""

import asyncio
import json
import uuid
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, Form, File, UploadFile
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse
from ..schemas.api import (
    ChatRequest,
    ChatResponse,
    ErrorResponse,
    SessionCreateResponse,
    SessionResponse,
)
from ..schemas.sketch import PlacedComponent
from ..services.redis_service import RedisService
from ..services.llm_service import LLMService
from ..agent.graph import create_agent_graph
from ..agent.state import AgentState
from ..utils.logger import get_logger
from ..utils.errors import AgentError, RedisError
from .dependencies import verify_api_key

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1", tags=["agent"])


# Services will be injected via dependency injection
# These will be set by main.py after services are initialized
_redis_service: Optional[RedisService] = None
_llm_service: Optional[LLMService] = None


def set_services(redis: RedisService, llm: LLMService) -> None:
    """Set the service instances (called from main.py)"""
    global _redis_service, _llm_service
    _redis_service = redis
    _llm_service = llm


def get_redis_service() -> RedisService:
    """Dependency to get Redis service"""
    if _redis_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Redis service not initialized",
        )
    return _redis_service


def get_llm_service() -> LLMService:
    """Dependency to get LLM service"""
    if _llm_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM service not initialized",
        )
    return _llm_service


@router.post("/session", response_model=SessionCreateResponse)
async def create_session(
    initial_sketch: list[PlacedComponent],
    redis: RedisService = Depends(get_redis_service),
    _: str = Depends(verify_api_key),
):
    """Create a new session"""
    try:
        session_id = await redis.create_session(initial_sketch)
        return SessionCreateResponse(
            sessionId=session_id,
            createdAt=datetime.utcnow().isoformat(),
        )
    except Exception as e:
        logger.error("Failed to create session", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create session: {str(e)}",
        )


@router.get("/session/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    redis: RedisService = Depends(get_redis_service),
    _: str = Depends(verify_api_key),
):
    """Get session state"""
    try:
        session_data = await redis.get_session(session_id)
        if not session_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found",
            )

        current_sketch = None
        if session_data.get("current_sketch"):
            current_sketch = [
                PlacedComponent(**comp) for comp in session_data["current_sketch"]
            ]

        return SessionResponse(
            sessionId=session_id,
            createdAt=session_data["created_at"],
            updatedAt=session_data["updated_at"],
            currentSketch=current_sketch,
            operationHistory=session_data.get("operation_history", []),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get session", error=str(e), session_id=session_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get session: {str(e)}",
        )


@router.delete("/session/{session_id}")
async def delete_session(
    session_id: str,
    redis: RedisService = Depends(get_redis_service),
    _: str = Depends(verify_api_key),
):
    """Delete a session"""
    try:
        await redis.delete_session(session_id)
        return {"success": True, "message": "Session deleted"}
    except Exception as e:
        logger.error("Failed to delete session", error=str(e), session_id=session_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete session: {str(e)}",
        )


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: Request,
    redis: RedisService = Depends(get_redis_service),
    llm: LLMService = Depends(get_llm_service),
    _: str = Depends(verify_api_key),
):
    """Chat endpoint - non-streaming, supports both JSON and multipart/form-data"""
    try:
        content_type = request.headers.get("content-type", "")

        # Handle multipart/form-data (with image)
        if "multipart/form-data" in content_type:
            form = await request.form()
            message = form.get("message", "")
            image_file: Optional[UploadFile] = form.get("image")
            session_id = form.get("sessionId")

            # Parse currentSketch from form
            current_sketch_json = form.get("currentSketch")
            if current_sketch_json:
                current_sketch = json.loads(current_sketch_json)
                current_sketch = [PlacedComponent(**comp) for comp in current_sketch]
            else:
                current_sketch = []

            # Parse messageHistory if present
            message_history_json = form.get("messageHistory")
            message_history = None
            if message_history_json:
                message_history = json.loads(message_history_json)

            # Read image data if present
            image_data = None
            image_format = None
            if image_file and image_file.filename:
                image_data = await image_file.read()
                image_format = "bytes"

            # Create ChatRequest-like object
            chat_request = ChatRequest(
                message=message,
                currentSketch=current_sketch,
                messageHistory=message_history,
                sessionId=session_id,
            )

            result = await _process_chat_request(chat_request, redis, llm, image_data, image_format)
            return result
        else:
            # Handle JSON request
            body = await request.json()
            request_obj = ChatRequest(**body)
            result = await _process_chat_request(request_obj, redis, llm)
            return result
    except AgentError as e:
        logger.error("Chat request failed", error=str(e), session_id=e.session_id or "")
        # Return a valid ChatResponse with error information
        # Fallback to empty sketch
        return ChatResponse(
            success=False,
            modifiedSketch=[],
            operations=[],
            reasoning=f"Error: {str(e)}",
            description=f"Request failed: {str(e)}",
            sessionId=e.session_id or "",
        )
    except Exception as e:
        logger.error("Chat request failed", error=str(e))
        # Return a valid ChatResponse with error information
        return ChatResponse(
            success=False,
            modifiedSketch=[],
            operations=[],
            reasoning=f"Error: {str(e)}",
            description=f"Request failed: {str(e)}",
            sessionId="",
        )


@router.post("/chat/stream")
async def chat_stream(
    request: ChatRequest,
    redis: RedisService = Depends(get_redis_service),
    llm: LLMService = Depends(get_llm_service),
    _: str = Depends(verify_api_key),
):
    """Chat endpoint with streaming responses"""
    async def event_generator():
        try:
            # Send analysis step
            yield {
                "event": "analysis",
                "data": json.dumps({"step": "analyzing", "status": "in_progress"}),
            }

            # Process request
            result = await _process_chat_request(request, redis, llm)

            # Send modification step
            yield {
                "event": "modification",
                "data": json.dumps({"step": "modifying", "status": "in_progress"}),
            }

            # Send validation step
            yield {
                "event": "validation",
                "data": json.dumps({"step": "validating", "status": "in_progress"}),
            }

            # Send execution step
            yield {
                "event": "execution",
                "data": json.dumps({"step": "executing", "status": "in_progress"}),
            }

            # Send final result
            yield {
                "event": "result",
                "data": json.dumps(result.model_dump(by_alias=True)),
            }
        except Exception as e:
            logger.error("Streaming error", error=str(e), session_id=request.session_id)
            yield {
                "event": "error",
                "data": json.dumps({
                    "success": False,
                    "error": str(e),
                    "sessionId": request.session_id,
                }),
            }

    return EventSourceResponse(event_generator())


async def _process_chat_request(
    request: ChatRequest,
    redis_service: RedisService,
    llm_service: LLMService,
    image_data: Optional[bytes] = None,
    image_format: Optional[str] = None,
) -> ChatResponse:
    """Process chat request using agent graph"""
    # Get or create session
    session_id = request.session_id
    if not session_id:
        session_id = await redis_service.create_session(request.current_sketch)
    else:
        # Extend session TTL
        await redis_service.extend_session_ttl(session_id)

    # Get session state
    session_data = await redis_service.get_session(session_id)
    if session_data:
        current_sketch_data = session_data.get("current_sketch")
        if current_sketch_data:
            current_sketch = [
                PlacedComponent(**comp) for comp in current_sketch_data
            ]
        else:
            current_sketch = request.current_sketch
        initial_sketch = [
            PlacedComponent(**comp) for comp in session_data.get("initial_sketch", [])
        ]
        latest_sketch = [
            PlacedComponent(**comp) for comp in session_data.get("latest_sketch", [])
        ]
    else:
        current_sketch = request.current_sketch
        initial_sketch = request.current_sketch
        latest_sketch = request.current_sketch

    # Create agent graph
    graph = create_agent_graph(llm_service)

    # Initialize state
    config = {"configurable": {"thread_id": session_id}}
    initial_state: AgentState = {
        "session_id": session_id,
        "user_message": request.message,
        "current_sketch": current_sketch,
        "message_history": request.message_history,
        "image_data": image_data,
        "image_format": image_format,
        "image_generated_components": None,
        "layout_analysis": None,
        "operations": None,
        "modification": None,
        "modified_sketch": None,
        "step": "image_analyze" if image_data else "analyze",
        "error": None,
        "initial_sketch": initial_sketch,
        "latest_sketch": latest_sketch,
        "retry_count": 0,
    }

    # Run graph
    try:
        final_state = None
        logger.debug(
            "Starting agent graph execution",
            session_id=session_id,
            has_image=image_data is not None,
            user_message=request.message[:100] if request.message else "",
            component_count=len(current_sketch),
        )
        async for state_dict in graph.astream(initial_state, config):
            # LangGraph returns a dict with node names as keys
            # Get the state from the last node that executed
            if isinstance(state_dict, dict):
                # Get the last node's state
                node_names = list(state_dict.keys())
                if node_names:
                    last_node = node_names[-1]
                    final_state = state_dict.get(last_node)
                    logger.debug(
                        "Graph node executed",
                        session_id=session_id,
                        node=last_node,
                        step=final_state.get("step") if final_state else None,
                    )
                    # Check for errors early
                    if final_state and final_state.get("step") == "error":
                        error_msg = final_state.get("error", "Unknown error")
                        logger.error(
                            "Agent graph error detected",
                            error=error_msg,
                            node=last_node,
                            session_id=session_id,
                        )
                        # Don't break, let it finish to get final state

        if not final_state:
            raise AgentError("Agent graph did not return a state", session_id)

        # Check for errors
        if final_state.get("step") == "error":
            error_msg = final_state.get("error", "Unknown error")
            # Fallback to latest sketch
            modified_sketch = final_state.get("latest_sketch") or final_state.get("initial_sketch")
            if modified_sketch:
                await redis_service.update_session(
                    session_id,
                    current_sketch=modified_sketch,
                )
            raise AgentError(error_msg, session_id)

        # Get modified sketch
        modified_sketch = final_state.get("modified_sketch")
        if not modified_sketch:
            # Fallback to latest sketch
            modified_sketch = final_state.get("latest_sketch") or final_state.get("initial_sketch")

        operations = final_state.get("operations", [])
        modification = final_state.get("modification")

        logger.info(
            "Agent graph execution complete",
            session_id=session_id,
            step=final_state.get("step"),
            operation_count=len(operations),
            has_modification=modification is not None,
        )

        # Update session (create if it doesn't exist)
        try:
            await redis_service.update_session(
                session_id,
                current_sketch=modified_sketch,
                operations=operations,
            )
        except RedisError as e:
            # If session doesn't exist, create it
            if "not found" in str(e).lower():
                logger.warning(
                    "Session not found during update, creating new session",
                    session_id=session_id,
                    error=str(e),
                )
                try:
                    await redis_service.create_session(modified_sketch, session_id)
                    logger.info("Recreated missing session", session_id=session_id)
                except Exception as create_err:
                    logger.error(
                        "Failed to recreate session",
                        session_id=session_id,
                        error=str(create_err),
                    )
                    # Don't fail the request if session update fails
            else:
                # Re-raise other Redis errors
                logger.error(
                    "Redis error during session update",
                    session_id=session_id,
                    error=str(e),
                )
                raise

        # Build response
        return ChatResponse(
            success=True,
            modifiedSketch=modified_sketch,
            operations=[op.model_dump() if hasattr(op, "model_dump") else op for op in operations],
            reasoning=modification.reasoning if modification else "No changes needed",
            description=modification.description if modification else "The current layout already satisfies the request",
            sessionId=session_id,
        )

    except AgentError as e:
        # Fallback to latest sketch
        latest = await redis_service.get_latest_sketch(session_id)
        if latest:
            try:
                await redis_service.update_session(session_id, current_sketch=latest)
            except RedisError:
                # Session might not exist, try to create it
                try:
                    await redis_service.create_session(latest, session_id)
                except Exception:
                    pass  # Ignore if creation also fails
        raise
    except Exception as e:
        logger.error("Agent execution failed", error=str(e), session_id=session_id)
        # Fallback to latest sketch
        latest = await redis_service.get_latest_sketch(session_id)
        if latest:
            try:
                await redis_service.update_session(session_id, current_sketch=latest)
            except RedisError:
                # Session might not exist, try to create it
                try:
                    await redis_service.create_session(latest, session_id)
                except Exception:
                    pass  # Ignore if creation also fails
        raise AgentError(f"Agent execution failed: {str(e)}", session_id)


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

