"""Operation executor - ported from TypeScript"""

import time
import random
import string
from typing import Optional
from ..schemas.sketch import PlacedComponent, ComponentOperation, ComponentType
from ..utils.errors import ValidationError, ExecutionError
from ..utils.logger import get_logger

logger = get_logger(__name__)


def validate_operations(
    current_sketch: list[PlacedComponent],
    operations: list[ComponentOperation],
) -> tuple[bool, Optional[str]]:
    """Validate operations before execution"""
    for i, operation in enumerate(operations):
        # Validate operation type
        if operation.type not in [
            "move",
            "resize",
            "add",
            "delete",
            "modify",
            "align",
            "distribute",
        ]:
            return False, f"Operation {i}: Invalid operation type '{operation.type}'"

        # Validate based on operation type
        if operation.type in ["move", "resize", "delete", "modify"]:
            if not operation.componentId:
                return False, f"Operation {i}: Missing componentId for {operation.type}"
            # Check if component exists
            if operation.type != "add":
                if not any(comp.id == operation.componentId for comp in current_sketch):
                    return False, f"Operation {i}: Component {operation.componentId} not found"

        if operation.type == "move":
            if operation.x is None or operation.y is None:
                return False, f"Operation {i}: Missing x or y for move operation"

        if operation.type == "resize":
            if operation.width is None or operation.height is None:
                return False, f"Operation {i}: Missing width or height for resize operation"
            if operation.width < 20:
                return False, f"Operation {i}: Width must be at least 20px"
            if operation.height < 2:
                return False, f"Operation {i}: Height must be at least 2px"

        if operation.type == "add":
            if not operation.componentType:
                return False, f"Operation {i}: Missing componentType for add operation"
            if operation.x is None or operation.y is None:
                return False, f"Operation {i}: Missing x or y for add operation"
            if operation.width is None or operation.height is None:
                return False, f"Operation {i}: Missing width or height for add operation"

        if operation.type in ["align", "distribute"]:
            if not operation.targetIds or len(operation.targetIds) < 2:
                return False, f"Operation {i}: Need at least 2 targetIds for {operation.type}"
            # Check if all target components exist
            for target_id in operation.targetIds:
                if not any(comp.id == target_id for comp in current_sketch):
                    return False, f"Operation {i}: Target component {target_id} not found"

        if operation.type == "align":
            if not operation.alignment:
                return False, f"Operation {i}: Missing alignment for align operation"

        if operation.type == "distribute":
            if operation.spacing is None:
                return False, f"Operation {i}: Missing spacing for distribute operation"

    return True, None


def execute_operations(
    current_sketch: list[PlacedComponent],
    operations: list[ComponentOperation],
) -> list[PlacedComponent]:
    """Execute operations on sketch"""
    # Validate first
    is_valid, error_msg = validate_operations(current_sketch, operations)
    if not is_valid:
        raise ValidationError(f"Operation validation failed: {error_msg}")

    sketch = [PlacedComponent(**comp.model_dump()) for comp in current_sketch]

    try:
        for operation in operations:
            if operation.type == "move":
                sketch = _execute_move(sketch, operation)
            elif operation.type == "resize":
                sketch = _execute_resize(sketch, operation)
            elif operation.type == "add":
                sketch = _execute_add(sketch, operation)
            elif operation.type == "delete":
                sketch = _execute_delete(sketch, operation)
            elif operation.type == "modify":
                sketch = _execute_modify(sketch, operation)
            elif operation.type == "align":
                sketch = _execute_align(sketch, operation)
            elif operation.type == "distribute":
                sketch = _execute_distribute(sketch, operation)

        return sketch
    except Exception as e:
        logger.error("Error executing operations", error=str(e), operation_type=operation.type)
        raise ExecutionError(f"Failed to execute operations: {str(e)}")


def _execute_move(
    sketch: list[PlacedComponent], operation: ComponentOperation
) -> list[PlacedComponent]:
    """Execute move operation"""
    if not operation.componentId or operation.x is None or operation.y is None:
        return sketch

    return [
        PlacedComponent(
            **{**comp.model_dump(), "x": operation.x, "y": operation.y}
        )
        if comp.id == operation.componentId
        else comp
        for comp in sketch
    ]


def _execute_resize(
    sketch: list[PlacedComponent], operation: ComponentOperation
) -> list[PlacedComponent]:
    """Execute resize operation"""
    if (
        not operation.componentId
        or operation.width is None
        or operation.height is None
    ):
        return sketch

    min_width = 20.0
    min_height = 20.0

    result = []
    for comp in sketch:
        if comp.id == operation.componentId:
            width = max(min_width, operation.width)
            height = (
                max(2.0, operation.height)
                if comp.type == ComponentType.HORIZONTAL_LINE
                else max(min_height, operation.height)
            )
            result.append(
                PlacedComponent(**{**comp.model_dump(), "width": width, "height": height})
            )
        else:
            result.append(comp)

    return result


def _execute_add(
    sketch: list[PlacedComponent], operation: ComponentOperation
) -> list[PlacedComponent]:
    """Execute add operation"""
    if (
        not operation.componentType
        or operation.x is None
        or operation.y is None
        or operation.width is None
        or operation.height is None
    ):
        return sketch

    # Generate unique ID
    new_id = f"component-{int(time.time() * 1000)}-{''.join(random.choices(string.ascii_lowercase + string.digits, k=9))}"
    min_width = 20.0
    min_height = 20.0

    try:
        comp_type = ComponentType(operation.componentType)
    except ValueError:
        raise ValidationError(f"Invalid component type: {operation.componentType}")

    width = max(min_width, operation.width)
    height = (
        max(2.0, operation.height)
        if comp_type == ComponentType.HORIZONTAL_LINE
        else max(min_height, operation.height)
    )

    new_component = PlacedComponent(
        id=new_id,
        type=comp_type,
        x=operation.x,
        y=operation.y,
        width=width,
        height=height,
        props=operation.props or {},
    )

    return sketch + [new_component]


def _execute_delete(
    sketch: list[PlacedComponent], operation: ComponentOperation
) -> list[PlacedComponent]:
    """Execute delete operation"""
    if not operation.componentId:
        return sketch

    return [comp for comp in sketch if comp.id != operation.componentId]


def _execute_modify(
    sketch: list[PlacedComponent], operation: ComponentOperation
) -> list[PlacedComponent]:
    """Execute modify operation"""
    if not operation.componentId or not operation.props:
        return sketch

    result = []
    for comp in sketch:
        if comp.id == operation.componentId:
            updated_props = {**comp.props, **operation.props}
            result.append(PlacedComponent(**{**comp.model_dump(), "props": updated_props}))
        else:
            result.append(comp)

    return result


def _execute_align(
    sketch: list[PlacedComponent], operation: ComponentOperation
) -> list[PlacedComponent]:
    """Execute align operation"""
    if (
        not operation.targetIds
        or not operation.alignment
        or len(operation.targetIds) < 2
    ):
        return sketch

    target_components = [comp for comp in sketch if comp.id in operation.targetIds]
    if len(target_components) < 2:
        return sketch

    result = []
    aligned_value: float

    if operation.alignment == "left":
        aligned_value = min(comp.x for comp in target_components)
        for comp in sketch:
            if comp.id in operation.targetIds:
                result.append(PlacedComponent(**{**comp.model_dump(), "x": aligned_value}))
            else:
                result.append(comp)

    elif operation.alignment == "right":
        aligned_value = max(comp.x + comp.width for comp in target_components)
        for comp in sketch:
            if comp.id in operation.targetIds:
                result.append(
                    PlacedComponent(**{**comp.model_dump(), "x": aligned_value - comp.width})
                )
            else:
                result.append(comp)

    elif operation.alignment == "center":
        aligned_value = sum(comp.x + comp.width / 2 for comp in target_components) / len(
            target_components
        )
        for comp in sketch:
            if comp.id in operation.targetIds:
                result.append(
                    PlacedComponent(**{**comp.model_dump(), "x": aligned_value - comp.width / 2})
                )
            else:
                result.append(comp)

    elif operation.alignment == "top":
        aligned_value = min(comp.y for comp in target_components)
        for comp in sketch:
            if comp.id in operation.targetIds:
                result.append(PlacedComponent(**{**comp.model_dump(), "y": aligned_value}))
            else:
                result.append(comp)

    elif operation.alignment == "bottom":
        aligned_value = max(comp.y + comp.height for comp in target_components)
        for comp in sketch:
            if comp.id in operation.targetIds:
                result.append(
                    PlacedComponent(**{**comp.model_dump(), "y": aligned_value - comp.height})
                )
            else:
                result.append(comp)

    else:
        return sketch

    return result


def _execute_distribute(
    sketch: list[PlacedComponent], operation: ComponentOperation
) -> list[PlacedComponent]:
    """Execute distribute operation"""
    if (
        not operation.targetIds
        or operation.spacing is None
        or len(operation.targetIds) < 2
    ):
        return sketch

    target_components = [comp for comp in sketch if comp.id in operation.targetIds]
    if len(target_components) < 2:
        return sketch

    # Sort by x position for horizontal distribution
    sorted_components = sorted(target_components, key=lambda c: c.x)
    first_x = sorted_components[0].x
    current_x = first_x

    updated_components = {}
    for comp in sorted_components:
        updated_components[comp.id] = PlacedComponent(**{**comp.model_dump(), "x": current_x})
        current_x += comp.width + operation.spacing

    result = []
    for comp in sketch:
        if comp.id in updated_components:
            result.append(updated_components[comp.id])
        else:
            result.append(comp)

    return result

