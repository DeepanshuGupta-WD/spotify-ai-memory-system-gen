"""
Authentication middleware/dependency — validates JWT and resolves user_id.

Dev mode (settings.debug + allow_dev_auth_header): accepts a plain
`X-User-Id` header so you can curl the API without minting a JWT while
building out the rest of the pipeline.
"""
from fastapi import Header, HTTPException, status
from jose import jwt, JWTError

from ...config import settings
from ...utils.exceptions import AuthenticationError
from ...utils.logger import get_logger

logger = get_logger(__name__)


async def authenticate_request(
   authorization: str | None = Header(default=None, alias="Authorization"),
    x_user_id: str | None = Header(default=None, alias="X-User-Id"),
) -> str:
    """FastAPI dependency: returns the resolved user_id or raises 401."""
    if settings.debug and settings.allow_dev_auth_header and x_user_id:
        logger.debug("Dev auth bypass: X-User-Id=%s", x_user_id)
        return x_user_id

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")

    token = authorization.removeprefix("Bearer ").strip()
    try:
        claims = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise AuthenticationError(str(exc)) from exc

    user_id = claims.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token missing 'sub' claim")
    return user_id
