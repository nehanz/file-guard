from fastapi import Request, status
from fastapi.responses import JSONResponse
from loguru import logger


class AppException(Exception):
    """
    Base application exception.
    """
    def __init__(self, message: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        self.message = message
        self.status_code = status_code


class NotFoundException(AppException):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message=message, status_code=status.HTTP_404_NOT_FOUND)


class ValidationException(AppException):
    def __init__(self, message: str = "Validation failed"):
        super().__init__(message=message, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Catch-all exception handler to return a standardized error response.
    """
    if isinstance(exc, AppException):
        logger.warning(f"AppException: {exc.message} at {request.url}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.message, "path": str(request.url)}
        )
    
    logger.error(f"Unhandled exception at {request.url}: {str(exc)}", exc_info=exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Internal server error", "path": str(request.url)}
    )
