from fastapi import Header, HTTPException, status

from .config import settings


def require_token(x_api_token: str | None = Header(default=None)) -> None:
    if x_api_token != settings.app_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API token")
