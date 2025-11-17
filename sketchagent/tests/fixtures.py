"""Test data fixtures"""

from app.schemas.sketch import PlacedComponent, ComponentType, ComponentOperation


def create_sample_sketch() -> list[PlacedComponent]:
    """Create a sample sketch with multiple components"""
    return [
        PlacedComponent(
            id="component-1",
            type=ComponentType.INPUT,
            x=100,
            y=50,
            width=300,
            height=40,
            props={},
        ),
        PlacedComponent(
            id="component-2",
            type=ComponentType.BUTTON,
            x=420,
            y=50,
            width=100,
            height=40,
            props={},
        ),
        PlacedComponent(
            id="component-3",
            type=ComponentType.IMAGE_PLACEHOLDER,
            x=100,
            y=110,
            width=420,
            height=200,
            props={},
        ),
    ]


def create_empty_sketch() -> list[PlacedComponent]:
    """Create an empty sketch"""
    return []


def create_single_component_sketch() -> list[PlacedComponent]:
    """Create a sketch with a single component"""
    return [
        PlacedComponent(
            id="component-1",
            type=ComponentType.CONTAINER,
            x=100,
            y=100,
            width=200,
            height=200,
            props={},
        ),
    ]


def create_large_sketch() -> list[PlacedComponent]:
    """Create a sketch with many components"""
    components = []
    for i in range(20):
        components.append(
            PlacedComponent(
                id=f"component-{i}",
                type=ComponentType.CONTAINER,
                x=100 + (i % 5) * 150,
                y=100 + (i // 5) * 150,
                width=120,
                height=120,
                props={},
            )
        )
    return components


def create_move_operation(component_id: str, x: float, y: float) -> ComponentOperation:
    """Create a move operation"""
    return ComponentOperation(
        type="move",
        componentId=component_id,
        x=x,
        y=y,
    )


def create_resize_operation(
    component_id: str, width: float, height: float
) -> ComponentOperation:
    """Create a resize operation"""
    return ComponentOperation(
        type="resize",
        componentId=component_id,
        width=width,
        height=height,
    )


def create_add_operation(
    component_type: str, x: float, y: float, width: float, height: float
) -> ComponentOperation:
    """Create an add operation"""
    return ComponentOperation(
        type="add",
        componentType=component_type,
        x=x,
        y=y,
        width=width,
        height=height,
    )


def create_delete_operation(component_id: str) -> ComponentOperation:
    """Create a delete operation"""
    return ComponentOperation(
        type="delete",
        componentId=component_id,
    )


def create_align_operation(
    target_ids: list[str], alignment: str
) -> ComponentOperation:
    """Create an align operation"""
    return ComponentOperation(
        type="align",
        targetIds=target_ids,
        alignment=alignment,
    )


def create_invalid_operation() -> ComponentOperation:
    """Create an invalid operation for testing"""
    return ComponentOperation(
        type="move",  # Missing required fields
        componentId=None,
        x=None,
        y=None,
    )

