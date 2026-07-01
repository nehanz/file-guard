import sys
from loguru import logger
from app.core.config import settings


def setup_logging() -> None:
    """
    Configure Loguru logging for the application.
    """
    logger.remove()
    
    logger.add(
        sys.stdout,
        enqueue=True,
        backtrace=True,
        level=settings.LOG_LEVEL,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
               "<level>{message}</level>",
    )
    
    logger.add(
        "logs/app.log",
        rotation="10 MB",
        retention="10 days",
        enqueue=True,
        backtrace=True,
        level=settings.LOG_LEVEL,
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}"
    )

    logger.info("Logging configured successfully.")
