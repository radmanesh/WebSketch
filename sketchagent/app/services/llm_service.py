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

            logger.debug(
                "Invoking LLM",
                session_id=session_id,
                system_prompt_length=len(system_prompt),
                user_prompt_length=len(user_prompt),
            )

            response = await self.model.ainvoke(messages)
            content = response.content if hasattr(response, "content") else str(response)

            logger.debug("LLM response received", session_id=session_id, response_length=len(content))

            return content
        except Exception as e:
            logger.error("LLM invocation failed", error=str(e), session_id=session_id)
            raise LLMError(f"LLM invocation failed: {str(e)}", session_id=session_id)

