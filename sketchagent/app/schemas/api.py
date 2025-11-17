"""API request/response models"""

from typing import Optional
from pydantic import BaseModel, Field
from .sketch import PlacedComponent, SketchModification


class ChatMessage(BaseModel):
    """Chat message"""
    role: str = Field(..., description="Message role: user, assistant, or system")
    content: str = Field(..., description="Message content")
    timestamp: Optional[str] = Field(None, description="Message timestamp")


class ChatRequest(BaseModel):
    """Chat API request"""
    message: str = Field(..., description="User message")
    current_sketch: list[PlacedComponent] = Field(..., alias="currentSketch", description="Current sketch state")
    message_history: Optional[list[ChatMessage]] = Field(
        None, alias="messageHistory", description="Previous conversation messages"
    )
    session_id: Optional[str] = Field(None, alias="sessionId", description="Session ID for state persistence")

    class Config:
        populate_by_name = True


class ChatResponse(BaseModel):
    """Chat API response"""
    success: bool = Field(..., description="Whether the request was successful")
    modified_sketch: list[PlacedComponent] = Field(..., alias="modifiedSketch", description="Modified sketch")
    operations: list = Field(..., description="Operations that were applied")
    reasoning: str = Field(..., description="Reasoning for the modifications")
    description: str = Field(..., description="Human-readable description")
    session_id: str = Field(..., alias="sessionId", description="Session ID")

    class Config:
        populate_by_name = True


class ErrorResponse(BaseModel):
    """Error response"""
    success: bool = Field(False, description="Always false for errors")
    error: str = Field(..., description="Error message")
    session_id: Optional[str] = Field(None, alias="sessionId", description="Session ID if available")

    class Config:
        populate_by_name = True


class SessionCreateResponse(BaseModel):
    """Session creation response"""
    session_id: str = Field(..., alias="sessionId", description="Created session ID")
    created_at: str = Field(..., alias="createdAt", description="Session creation timestamp")

    class Config:
        populate_by_name = True


class SessionResponse(BaseModel):
    """Session state response"""
    session_id: str = Field(..., alias="sessionId", description="Session ID")
    created_at: str = Field(..., alias="createdAt", description="Creation timestamp")
    updated_at: str = Field(..., alias="updatedAt", description="Last update timestamp")
    current_sketch: Optional[list[PlacedComponent]] = Field(
        None, alias="currentSketch", description="Current sketch state"
    )
    operation_history: Optional[list] = Field(
        None, alias="operationHistory", description="History of operations for undo/redo"
    )

    class Config:
        populate_by_name = True

