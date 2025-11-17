"""LLM service with retry logic"""

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

