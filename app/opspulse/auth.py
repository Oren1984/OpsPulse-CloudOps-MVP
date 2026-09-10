import hmac

from fastapi import Header, HTTPException, status

from opspulse.config import settings


async def require_api_key(
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
) -> str:
    if x_api_key is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")

    configured_key = settings.api_key
    if not configured_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API key is not configured",
        )

    if not hmac.compare_digest(x_api_key, configured_key):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    return x_api_key
