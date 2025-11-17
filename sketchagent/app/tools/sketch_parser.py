"""Sketch layout parser - ported from TypeScript"""

from typing import TypedDict, Optional
from ..schemas.sketch import PlacedComponent


class ComponentDescription(TypedDict):
    """Component description"""
    id: str
    type: str
    position: str
    size: str
    description: str


class SpatialRelationship(TypedDict, total=False):
    """Spatial relationship between components"""
    component1: str
    component2: str
    relationship: str  # 'above' | 'below' | 'left' | 'right' | 'overlapping' | 'aligned'
    distance: Optional[float]


class ComponentGroup(TypedDict):
    """Component group"""
    components: list[str]
    bounds: dict[str, float]  # {x, y, width, height}


class LayoutStats(TypedDict, total=False):
    """Layout statistics"""
    canvasWidth: float
    canvasHeight: float
    componentCount: int
    componentTypes: dict[str, int]
    leftColumn: Optional[ComponentGroup]
    rightColumn: Optional[ComponentGroup]
    topSection: Optional[ComponentGroup]
    bottomSection: Optional[ComponentGroup]


class LayoutAnalysis(TypedDict):
    """Complete layout analysis"""
    description: str
    components: list[ComponentDescription]
    spatialRelationships: list[SpatialRelationship]
    layoutStats: LayoutStats


def parse_sketch_layout(components: list[PlacedComponent]) -> LayoutAnalysis:
    """Parse and analyze sketch layout"""
    if not components:
        return {
            "description": "Empty sketch with no components",
            "components": [],
            "spatialRelationships": [],
            "layoutStats": {
                "canvasWidth": 0,
                "canvasHeight": 0,
                "componentCount": 0,
                "componentTypes": {},
            },
        }

    # Calculate canvas bounds
    bounds = _calculate_bounds(components)

    # Generate component descriptions
    component_descriptions = [_describe_component(comp, bounds) for comp in components]

    # Identify spatial relationships
    relationships = _identify_relationships(components)

    # Analyze layout structure
    stats = _analyze_layout(components, bounds)

    # Generate overall description
    description = _generate_description(components, stats, relationships)

    return {
        "description": description,
        "components": component_descriptions,
        "spatialRelationships": relationships,
        "layoutStats": stats,
    }


def _calculate_bounds(components: list[PlacedComponent]) -> dict[str, float]:
    """Calculate canvas bounds"""
    min_x = min(comp.x for comp in components)
    min_y = min(comp.y for comp in components)
    max_x = max(comp.x + comp.width for comp in components)
    max_y = max(comp.y + comp.height for comp in components)

    return {"minX": min_x, "minY": min_y, "maxX": max_x, "maxY": max_y}


def _describe_component(
    component: PlacedComponent, bounds: dict[str, float]
) -> ComponentDescription:
    """Describe a component's position and size"""
    canvas_width = bounds["maxX"] - bounds["minX"]
    canvas_height = bounds["maxY"] - bounds["minY"]

    x_percent = ((component.x - bounds["minX"]) / canvas_width * 100) if canvas_width > 0 else 0
    y_percent = ((component.y - bounds["minY"]) / canvas_height * 100) if canvas_height > 0 else 0

    # Determine position
    if component.x < canvas_width * 0.33:
        position = "left side"
    elif component.x > canvas_width * 0.66:
        position = "right side"
    else:
        position = "center"

    if component.y < canvas_height * 0.33:
        position += ", top section"
    elif component.y > canvas_height * 0.66:
        position += ", bottom section"
    else:
        position += ", middle section"

    size = f"{int(component.width)}x{int(component.height)}px"

    return {
        "id": component.id,
        "type": component.type.value,
        "position": position,
        "size": size,
        "description": f"{component.type.value} at {position} ({x_percent:.1f}%, {y_percent:.1f}%), size {size}",
    }


def _identify_relationships(components: list[PlacedComponent]) -> list[SpatialRelationship]:
    """Identify spatial relationships between components"""
    relationships: list[SpatialRelationship] = []
    threshold = 20.0  # pixels

    for i in range(len(components)):
        for j in range(i + 1, len(components)):
            comp1 = components[i]
            comp2 = components[j]

            # Check for overlapping
            if _is_overlapping(comp1, comp2):
                relationships.append({
                    "component1": comp1.id,
                    "component2": comp2.id,
                    "relationship": "overlapping",
                })
                continue

            # Check vertical relationships
            vertical_distance = abs(
                (comp1.y + comp1.height / 2) - (comp2.y + comp2.height / 2)
            )
            horizontal_overlap = max(
                0,
                min(comp1.x + comp1.width, comp2.x + comp2.width)
                - max(comp1.x, comp2.x),
            )

            if horizontal_overlap > min(comp1.width, comp2.width) * 0.5:
                if comp1.y + comp1.height < comp2.y:
                    relationships.append({
                        "component1": comp1.id,
                        "component2": comp2.id,
                        "relationship": "above",
                        "distance": comp2.y - (comp1.y + comp1.height),
                    })
                elif comp2.y + comp2.height < comp1.y:
                    relationships.append({
                        "component1": comp1.id,
                        "component2": comp2.id,
                        "relationship": "below",
                        "distance": comp1.y - (comp2.y + comp2.height),
                    })

            # Check horizontal relationships
            vertical_overlap = max(
                0,
                min(comp1.y + comp1.height, comp2.y + comp2.height)
                - max(comp1.y, comp2.y),
            )

            if vertical_overlap > min(comp1.height, comp2.height) * 0.5:
                if comp1.x + comp1.width < comp2.x:
                    relationships.append({
                        "component1": comp1.id,
                        "component2": comp2.id,
                        "relationship": "left",
                        "distance": comp2.x - (comp1.x + comp1.width),
                    })
                elif comp2.x + comp2.width < comp1.x:
                    relationships.append({
                        "component1": comp1.id,
                        "component2": comp2.id,
                        "relationship": "right",
                        "distance": comp1.x - (comp2.x + comp2.width),
                    })

            # Check alignment
            if abs(comp1.x - comp2.x) < threshold:
                relationships.append({
                    "component1": comp1.id,
                    "component2": comp2.id,
                    "relationship": "aligned",
                })

    return relationships


def _is_overlapping(comp1: PlacedComponent, comp2: PlacedComponent) -> bool:
    """Check if two components overlap"""
    return not (
        comp1.x + comp1.width < comp2.x
        or comp2.x + comp2.width < comp1.x
        or comp1.y + comp1.height < comp2.y
        or comp2.y + comp2.height < comp1.y
    )


def _analyze_layout(
    components: list[PlacedComponent], bounds: dict[str, float]
) -> LayoutStats:
    """Analyze layout structure"""
    canvas_width = bounds["maxX"] - bounds["minX"]
    canvas_height = bounds["maxY"] - bounds["minY"]
    component_types: dict[str, int] = {}

    for comp in components:
        comp_type = comp.type.value
        component_types[comp_type] = component_types.get(comp_type, 0) + 1

    # Identify columns
    mid_x = bounds["minX"] + canvas_width / 2
    left_components = [
        comp.id for comp in components if comp.x + comp.width / 2 < mid_x
    ]
    right_components = [
        comp.id for comp in components if comp.x + comp.width / 2 >= mid_x
    ]

    left_column = None
    if left_components:
        left_comps = [c for c in components if c.id in left_components]
        left_column = {
            "components": left_components,
            "bounds": _calculate_group_bounds(left_comps),
        }

    right_column = None
    if right_components:
        right_comps = [c for c in components if c.id in right_components]
        right_column = {
            "components": right_components,
            "bounds": _calculate_group_bounds(right_comps),
        }

    # Identify top and bottom sections
    mid_y = bounds["minY"] + canvas_height / 2
    top_components = [
        comp.id for comp in components if comp.y + comp.height / 2 < mid_y
    ]
    bottom_components = [
        comp.id for comp in components if comp.y + comp.height / 2 >= mid_y
    ]

    top_section = None
    if top_components:
        top_comps = [c for c in components if c.id in top_components]
        top_section = {
            "components": top_components,
            "bounds": _calculate_group_bounds(top_comps),
        }

    bottom_section = None
    if bottom_components:
        bottom_comps = [c for c in components if c.id in bottom_components]
        bottom_section = {
            "components": bottom_components,
            "bounds": _calculate_group_bounds(bottom_comps),
        }

    stats: LayoutStats = {
        "canvasWidth": canvas_width,
        "canvasHeight": canvas_height,
        "componentCount": len(components),
        "componentTypes": component_types,
    }

    if left_column:
        stats["leftColumn"] = left_column
    if right_column:
        stats["rightColumn"] = right_column
    if top_section:
        stats["topSection"] = top_section
    if bottom_section:
        stats["bottomSection"] = bottom_section

    return stats


def _calculate_group_bounds(components: list[PlacedComponent]) -> dict[str, float]:
    """Calculate bounds for a group of components"""
    if not components:
        return {"x": 0, "y": 0, "width": 0, "height": 0}

    min_x = min(comp.x for comp in components)
    min_y = min(comp.y for comp in components)
    max_x = max(comp.x + comp.width for comp in components)
    max_y = max(comp.y + comp.height for comp in components)

    return {
        "x": min_x,
        "y": min_y,
        "width": max_x - min_x,
        "height": max_y - min_y,
    }


def _generate_description(
    components: list[PlacedComponent],
    stats: LayoutStats,
    relationships: list[SpatialRelationship],
) -> str:
    """Generate overall layout description"""
    parts: list[str] = []

    parts.append(f"The sketch contains {stats['componentCount']} components:")

    for comp_type, count in stats["componentTypes"].items():
        parts.append(f"- {count} {comp_type}{'s' if count > 1 else ''}")

    if stats.get("leftColumn") and stats.get("rightColumn"):
        left_count = len(stats["leftColumn"]["components"])
        right_count = len(stats["rightColumn"]["components"])
        parts.append(
            f"The layout has two columns: left column with {left_count} components, "
            f"right column with {right_count} components."
        )

    if stats.get("topSection") and stats.get("bottomSection"):
        top_count = len(stats["topSection"]["components"])
        bottom_count = len(stats["bottomSection"]["components"])
        parts.append(
            f"The layout is divided into top section ({top_count} components) "
            f"and bottom section ({bottom_count} components)."
        )

    alignment_count = sum(
        1 for r in relationships if r.get("relationship") == "aligned"
    )
    if alignment_count > 0:
        parts.append(f"There are {alignment_count} aligned component pairs.")

    return " ".join(parts)

