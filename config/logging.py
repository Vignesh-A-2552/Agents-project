import sys
import os
from pathlib import Path
from loguru import logger


def setup_logging():
    """Configure loguru logging for the application."""
    
    # Ensure logs directory exists
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Remove default handler
    logger.remove()
    
    # Determine log level based on environment
    console_level = "DEBUG" if os.getenv("DEBUG", "false").lower() == "true" else "INFO"
    
    # Add console handler with custom format
    logger.add(
        sys.stdout,
        level=console_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True,
        backtrace=True,
        diagnose=True,
        catch=True
    )
    
    # Add file handler for all logs
    logger.add(
        "logs/app.log",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="1 day",
        retention="30 days",
        compression="zip",
        backtrace=True,
        diagnose=True
    )
    
    # Add separate error log file
    logger.add(
        "logs/error.log",
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="1 week",
        retention="90 days",
        compression="zip",
        backtrace=True,
        diagnose=True
    )
    
    # Add request/response log file
    logger.add(
        "logs/requests.log",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
        rotation="1 day",
        retention="7 days",
        filter=lambda record: "REQUEST" in record["message"] or "RESPONSE" in record["message"],
        backtrace=False,
        diagnose=False
    )
    
    # Add error handler for uncaught exceptions
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    
    sys.excepthook = handle_exception
    
    logger.info(f"Logging system initialized - Console level: {console_level}")
    logger.debug("Debug logging enabled")
    return logger


def get_logger(name: str = None):
    """Get a logger instance with optional name."""
    if name:
        return logger.bind(name=name)
    return logger