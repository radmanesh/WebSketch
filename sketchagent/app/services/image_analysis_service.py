"""Image analysis service for layout detection"""

import json
import base64
from io import BytesIO
from typing import List, Optional
import cv2
import numpy as np
from PIL import Image
from ..schemas.sketch import PlacedComponent, ComponentType
from ..services.llm_service import LLMService
from ..utils.logger import get_logger
from ..utils.errors import AgentError

logger = get_logger(__name__)


class ImageAnalysisService:
    """Service for analyzing images and generating wireframe components"""

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    async def analyze_image(
        self, image_data: bytes, image_format: str = "bytes", session_id: Optional[str] = None
    ) -> List[PlacedComponent]:
        """
        Analyze image and generate wireframe components using hybrid approach:
        1. OpenCV for edge detection and bounding box detection
        2. GPT-4 Vision for semantic understanding
        """
        try:
            # Convert image data to numpy array for OpenCV
            if image_format == "base64":
                if isinstance(image_data, bytes):
                    image_bytes = base64.b64decode(image_data)
                else:
                    image_bytes = base64.b64decode(image_data.encode("utf-8"))
            else:
                image_bytes = image_data

            # Load image with PIL first to handle various formats
            pil_image = Image.open(BytesIO(image_bytes))
            # Convert to RGB if needed
            if pil_image.mode != "RGB":
                pil_image = pil_image.convert("RGB")

            # Convert to numpy array for OpenCV
            img_array = np.array(pil_image)
            # Convert RGB to BGR for OpenCV
            cv_image = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            image_height, image_width = cv_image.shape[:2]

            # Step 1: Use OpenCV to detect bounding boxes
            bounding_boxes = self._detect_bounding_boxes(cv_image)

            # Step 2: Use GPT-4 Vision to understand semantic meaning
            # Convert image back to base64 for vision model
            buffered = BytesIO()
            pil_image.save(buffered, format="JPEG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

            # Get semantic analysis from vision model
            semantic_analysis = await self._analyze_with_vision(
                img_base64, bounding_boxes, image_width, image_height, session_id
            )

            # Step 3: Combine OpenCV bounding boxes with semantic analysis
            components = self._combine_detections(
                bounding_boxes, semantic_analysis, image_width, image_height
            )

            logger.info(
                "Image analysis complete",
                session_id=session_id,
                component_count=len(components),
                image_width=image_width,
                image_height=image_height,
            )

            return components

        except Exception as e:
            logger.error("Image analysis failed", error=str(e), session_id=session_id, exc_info=True)
            raise AgentError(f"Image analysis failed: {str(e)}", session_id)

    def _detect_bounding_boxes(self, cv_image: np.ndarray) -> List[dict]:
        """Use OpenCV to detect bounding boxes of UI elements"""
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)

        # Apply edge detection
        edges = cv2.Canny(gray, 50, 150)

        # Apply morphological operations to close gaps
        kernel = np.ones((3, 3), np.uint8)
        edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        bounding_boxes = []
        min_area = 100  # Minimum area to consider (filter out noise)

        for contour in contours:
            area = cv2.contourArea(contour)
            if area < min_area:
                continue

            x, y, w, h = cv2.boundingRect(contour)
            # Filter out very small or very large boxes
            if w < 20 or h < 20:
                continue
            if w > cv_image.shape[1] * 0.95 or h > cv_image.shape[0] * 0.95:
                continue

            bounding_boxes.append(
                {
                    "x": float(x),
                    "y": float(y),
                    "width": float(w),
                    "height": float(h),
                    "area": float(area),
                }
            )

        # Sort by area (largest first) and limit to top 50
        bounding_boxes.sort(key=lambda b: b["area"], reverse=True)
        bounding_boxes = bounding_boxes[:50]

        return bounding_boxes

    async def _analyze_with_vision(
        self,
        image_base64: str,
        bounding_boxes: List[dict],
        image_width: int,
        image_height: int,
        session_id: Optional[str] = None,
    ) -> dict:
        """Use GPT-4 Vision to understand semantic meaning of detected regions"""

        system_prompt = """You are an expert at analyzing UI layouts and wireframes.
Analyze the provided image and the detected bounding boxes to understand what UI components they represent.

For each bounding box, identify:
- Component type (Container, Button, Input, ImagePlaceholder, Text, Heading, NavigationBox, List, Table, HorizontalLine, Footer)
- Semantic meaning (what the component is/does)
- Any additional properties that might be relevant

Return a JSON object with this structure:
{
  "components": [
    {
      "index": 0,
      "componentType": "Button",
      "semanticMeaning": "Submit button",
      "confidence": 0.9,
      "properties": {}
    }
  ],
  "layoutDescription": "Overall description of the layout"
}

Be accurate and only identify components you're confident about."""

        user_prompt = f"""Analyze this UI image (width: {image_width}px, height: {image_height}px).

Detected bounding boxes:
{json.dumps(bounding_boxes, indent=2)}

For each bounding box, identify what UI component it represents. Consider:
- Position and size relative to the image
- Visual appearance (if you can see it)
- Context within the layout
- Common UI patterns

Return the JSON analysis as specified."""

        try:
            # Convert base64 string to bytes for the vision model
            image_bytes = base64.b64decode(image_base64.encode("utf-8"))

            response = await self.llm_service.invoke_with_image(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                image_data=image_bytes,
                image_format="bytes",
                session_id=session_id,
            )

            # Parse JSON response (handle markdown code blocks)
            response = response.strip()
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()

            analysis = json.loads(response)
            return analysis

        except json.JSONDecodeError as e:
            logger.warning(
                "Failed to parse vision model response as JSON, using fallback",
                error=str(e),
                session_id=session_id,
            )
            # Fallback: return empty analysis
            return {"components": [], "layoutDescription": "Analysis failed"}

    def _combine_detections(
        self,
        bounding_boxes: List[dict],
        semantic_analysis: dict,
        image_width: int,
        image_height: int,
    ) -> List[PlacedComponent]:
        """Combine OpenCV bounding boxes with semantic analysis to create components"""

        components = []
        semantic_components = semantic_analysis.get("components", [])

        # Create a mapping from index to semantic info
        semantic_map = {comp.get("index", i): comp for i, comp in enumerate(semantic_components)}

        import time
        import random

        for i, bbox in enumerate(bounding_boxes):
            # Get semantic info for this box
            semantic_info = semantic_map.get(i, {})

            # Determine component type
            component_type_str = semantic_info.get("componentType", "Container")
            try:
                component_type = ComponentType(component_type_str)
            except ValueError:
                # Fallback to Container if type is invalid
                component_type = ComponentType.CONTAINER

            # Generate unique ID
            component_id = f"component-{int(time.time() * 1000)}-{random.randint(1000, 9999)}"

            # Create component
            component = PlacedComponent(
                id=component_id,
                type=component_type,
                x=bbox["x"],
                y=bbox["y"],
                width=bbox["width"],
                height=bbox["height"],
                props=semantic_info.get("properties", {}),
            )

            components.append(component)

        return components

