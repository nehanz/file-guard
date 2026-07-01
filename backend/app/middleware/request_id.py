import uuid
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from loguru import logger
import contextvars

# Context variable to store request ID for the current async task
request_id_var = contextvars.ContextVar("request_id", default="UNKNOWN")

class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware to assign a unique UUID to each request.
    """
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request_id_var.set(request_id)
        
        with logger.contextualize(request_id=request_id):
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            return response
