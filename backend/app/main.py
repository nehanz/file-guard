from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.exceptions import global_exception_handler, AppException
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.timing import TimingMiddleware
from app.api.router import api_router
from app.database.connection import DatabaseConnection
from app.dependencies.container import Container


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events.
    """
    setup_logging()
    logger.info("Starting up application...")
    
    # Connect to Database
    await DatabaseConnection.connect()
    
    yield
    
    # Disconnect Database
    logger.info("Shutting down application...")
    await DatabaseConnection.disconnect()


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    """
    # Setup dependency injection container
    container = Container()
    
    # Initialize FastAPI application
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url=f"{settings.API_V1_STR}/docs",
        redoc_url=f"{settings.API_V1_STR}/redoc",
        lifespan=lifespan
    )
    
    # Attach container to application for wiring
    app.container = container
    
    # Add CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add Custom Middlewares (order matters: bottom one runs first during request)
    app.add_middleware(TimingMiddleware)
    app.add_middleware(RequestIDMiddleware)
    
    # Register Global Exception Handlers
    app.add_exception_handler(AppException, global_exception_handler)
    app.add_exception_handler(Exception, global_exception_handler)
    
    # Include Main API Router
    app.include_router(api_router, prefix=settings.API_V1_STR)
    
    return app


app = create_app()
