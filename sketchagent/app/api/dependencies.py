"""FastAPI dependencies"""

from fastapi import Header, HTTPException, status
from ..config import settings


async def verify_api_key(x_api_key: str = Header(..., alias="X-API-Key")) -> str:
    """Verify API key"""
    if not settings.api_key:
        # If no API key is configured, allow all requests (development mode)
        return "dev"

    if x_api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
    return x_api_key

