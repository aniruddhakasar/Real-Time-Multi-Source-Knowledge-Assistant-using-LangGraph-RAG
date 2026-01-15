"""Centralized logging configuration for the RAG system.

Provides structured logging with:
- Multiple handlers (console, file)
- Proper formatting
- Log rotation
- Performance tracking
- Error tracking
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from datetime import datetime

# Create logs directory
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)


def configure_logging(
    name: str = "rag_system",
    level: int = logging.INFO,
    log_file: bool = True
) -> logging.Logger:
    """Configure logging for the application.

    Args:
        name: Logger name
        level: Logging level
        log_file: Whether to log to file

    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Prevent duplicate handlers
    if logger.handlers:
        return logger

    # Format
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (rotating)
    if log_file:
        log_file_path = LOGS_DIR / f"{name}.log"
        file_handler = logging.handlers.RotatingFileHandler(
            log_file_path,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


# Module-level logger
logger = configure_logging()


def log_performance(func):
    """Decorator for logging function execution time.

    Args:
        func: Function to decorate

    Returns:
        Decorated function
    """
    def wrapper(*args, **kwargs):
        import time
        start = time.time()
        logger.debug(f"Executing {func.__name__}")
        try:
            result = func(*args, **kwargs)
            elapsed = time.time() - start
            logger.info(f"{func.__name__} completed in {elapsed:.2f}s")
            return result
        except Exception as e:
            elapsed = time.time() - start
            logger.error(f"{func.__name__} failed after {elapsed:.2f}s: {e}")
            raise
    return wrapper


def log_error(error: Exception, context: str = ""):
    """Log error with context.

    Args:
        error: Exception to log
        context: Additional context
    """
    logger.error(f"Error {context}: {type(error).__name__}: {str(error)}")


class PerformanceTracker:
    """Track performance metrics."""

    def __init__(self):
        """Initialize tracker."""
        self.metrics = {}

    def start(self, key: str):
        """Start timing a metric.

        Args:
            key: Metric key
        """
        import time
        self.metrics[key] = {"start": time.time()}

    def end(self, key: str) -> float:
        """End timing a metric.

        Args:
            key: Metric key

        Returns:
            Elapsed time
        """
        import time
        if key not in self.metrics:
            return 0
        
        elapsed = time.time() - self.metrics[key]["start"]
        self.metrics[key]["elapsed"] = elapsed
        logger.info(f"Performance: {key} took {elapsed:.2f}s")
        return elapsed

    def get_metrics(self) -> dict:
        """Get all metrics.

        Returns:
            Metrics dictionary
        """
        return self.metrics


# Global tracker
tracker = PerformanceTracker()
