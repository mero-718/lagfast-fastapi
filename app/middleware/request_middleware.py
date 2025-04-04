from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from .auth_middleware import JWTBearer
import re

# List of paths that don't require authentication
PUBLIC_PATHS = [
    r"^/auth/login",
    r"^/auth/register"
]

jwt_bearer = JWTBearer()

async def auth_middleware(request: Request, call_next):
    # Check if the path is public
    path = request.url.path
    if any(re.match(pattern, path) for pattern in PUBLIC_PATHS):
        return await call_next(request)

    try:
        # Verify the token
        token = await jwt_bearer(request)
        # Add the token to the request state for use in route handlers
        request.state.token = token
        return await call_next(request)
    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={"detail": e.detail}
        ) 