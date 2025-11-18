"""LLM service with retry logic"""

import base64
from typing import Optional
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from ..utils.logger import get_logger
from ..utils.errors import LLMError
from ..utils.debug_logger import log_llm_request, log_llm_response

logger = get_logger(__name__)


class LLMService:
    """LLM service with retry and error handling"""

    def __init__(self, api_key: str, model_name: str = "gpt-4o-mini", temperature: float = 0.3):
        self.model = ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            openai_api_key=api_key,
        )
        # Vision model for image analysis (gpt-4o or gpt-4o-mini with vision support)
        self.vision_model = ChatOpenAI(
            model_name="gpt-4o",
            temperature=temperature,
            openai_api_key=api_key,
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((LLMError, Exception)),
        reraise=True,
    )
    async def invoke(
        self, system_prompt: str, user_prompt: str, session_id: Optional[str] = None
    ) -> str:
        """Invoke LLM with retry logic"""
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt),
            ]

            log_llm_request(len(system_prompt), len(user_prompt), session_id)

            response = await self.model.ainvoke(messages)
            content = response.content if hasattr(response, "content") else str(response)

            log_llm_response(len(content), session_id, has_json="{" in content)

            return content
        except Exception as e:
            logger.error("LLM invocation failed", error=str(e), session_id=session_id)
            raise LLMError(f"LLM invocation failed: {str(e)}", session_id=session_id)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((LLMError, Exception)),
        reraise=True,
    )
    async def invoke_with_image(
        self,
        system_prompt: str,
        user_prompt: str,
        image_data: bytes,
        image_format: str = "base64",
        session_id: Optional[str] = None,
    ) -> str:
        """Invoke vision model with image data"""
        try:
            # Convert image bytes to base64 if needed
            if image_format == "bytes":
                image_base64 = base64.b64encode(image_data).decode("utf-8")
            elif image_format == "base64":
                # Assume image_data is already base64 encoded bytes
                if isinstance(image_data, bytes):
                    image_base64 = image_data.decode("utf-8")
                else:
                    image_base64 = str(image_data)
            else:
                raise ValueError(f"Unsupported image format: {image_format}")

            # Create image URL for vision model
            image_url = f"data:image/jpeg;base64,{image_base64}"

            # Create messages with image
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(
                    content=[
                        {"type": "text", "text": user_prompt},
                        {"type": "image_url", "image_url": {"url": image_url}},
                    ]
                ),
            ]

            log_llm_request(len(system_prompt), len(user_prompt), session_id, has_image=True)

            response = await self.vision_model.ainvoke(messages)
            content = response.content if hasattr(response, "content") else str(response)

            log_llm_response(len(content), session_id, has_json="{" in content)

            return content
        except Exception as e:
            logger.error("Vision model invocation failed", error=str(e), session_id=session_id)
            raise LLMError(f"Vision model invocation failed: {str(e)}", session_id=session_id)

