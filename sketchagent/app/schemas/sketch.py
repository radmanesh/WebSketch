"""Sketch data models matching TypeScript types"""

from enum import Enum
from typing import Literal, Optional
from pydantic import BaseModel, Field, field_validator


class ComponentType(str, Enum):
    """Component types matching TypeScript ComponentType"""
    CONTAINER = "Container"
    BUTTON = "Button"
    INPUT = "Input"
    IMAGE_PLACEHOLDER = "ImagePlaceholder"
    TEXT = "Text"
    HORIZONTAL_LINE = "HorizontalLine"
    HEADING = "Heading"
    FOOTER = "Footer"
    NAVIGATION_BOX = "NavigationBox"
    LIST = "List"
    TABLE = "Table"


class PlacedComponent(BaseModel):
    """Placed component matching TypeScript PlacedComponent"""
    id: str = Field(..., description="Unique component identifier")
    type: ComponentType = Field(..., description="Component type")
    x: float = Field(..., ge=0, description="X coordinate in pixels")
    y: float = Field(..., ge=0, description="Y coordinate in pixels")
    width: float = Field(..., gt=0, description="Width in pixels")
    height: float = Field(..., gt=0, description="Height in pixels")
    props: dict = Field(default_factory=dict, description="Additional properties")

    @field_validator("width")
    @classmethod
    def validate_width(cls, v: float) -> float:
        """Ensure minimum width of 20px"""
        return max(20.0, v)

    @field_validator("height")
    @classmethod
    def validate_height(cls, v: float, info) -> float:
        """Ensure minimum height (2px for HorizontalLine, 20px for others)"""
        if info.data.get("type") == ComponentType.HORIZONTAL_LINE:
            return max(2.0, v)
        return max(20.0, v)


class ComponentOperation(BaseModel):
    """Component operation matching TypeScript ComponentOperation"""
    type: Literal[
        "move", "resize", "add", "delete", "modify", "align", "distribute", "replace"
    ] = Field(..., description="Operation type")
    componentId: Optional[str] = Field(None, description="Target component ID")
    componentType: Optional[str] = Field(None, description="Component type for add operations")
    x: Optional[float] = Field(None, description="X coordinate")
    y: Optional[float] = Field(None, description="Y coordinate")
    width: Optional[float] = Field(None, description="Width")
    height: Optional[float] = Field(None, description="Height")
    props: Optional[dict] = Field(None, description="Properties")
    targetIds: Optional[list[str]] = Field(None, description="Target IDs for multi-component operations")
    alignment: Optional[Literal["left", "right", "center", "top", "bottom"]] = Field(
        None, description="Alignment type"
    )
    spacing: Optional[float] = Field(None, description="Spacing for distribution")
    components: Optional[list[PlacedComponent]] = Field(None, description="Components for replace operation")


class SketchModification(BaseModel):
    """Sketch modification result"""
    operations: list[ComponentOperation] = Field(..., description="List of operations to perform")
    reasoning: str = Field(..., description="Brief explanation of why these operations were chosen")
    description: str = Field(..., description="Human-readable description of what will change")

