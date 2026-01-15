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


def setup_chat_logger() -> logging.Logger:
    """Set up dedicated logger for chat sessions and interactions.

    Returns:
        Configured chat logger
    """
    chat_logger = logging.getLogger("chat_sessions")
    chat_logger.setLevel(logging.INFO)

    # Prevent duplicate handlers
    if chat_logger.handlers:
        return chat_logger

    # Create chat logs directory
    chat_logs_dir = LOGS_DIR / "chat_sessions"
    chat_logs_dir.mkdir(exist_ok=True)

    # Detailed format for chat logs
    chat_formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)s | Session:%(session_id)s | User:%(user_id)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # File handler for chat logs (daily rotation)
    chat_log_file = chat_logs_dir / "chat_sessions.log"
    chat_file_handler = logging.handlers.TimedRotatingFileHandler(
        chat_log_file,
        when='midnight',  # Rotate at midnight
        interval=1,       # Every 1 day
        backupCount=30    # Keep 30 days of logs
    )
    chat_file_handler.setLevel(logging.INFO)
    chat_file_handler.setFormatter(chat_formatter)
    chat_logger.addHandler(chat_file_handler)

    # Also add to main logger for console output during development
    if logger.level <= logging.DEBUG:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(chat_formatter)
        chat_logger.addHandler(console_handler)

    # Prevent propagation to root logger to avoid duplicate logs
    chat_logger.propagate = False

    return chat_logger


# Global chat logger
chat_logger = setup_chat_logger()


def log_chat_interaction(session_id: str, user_id: str, user_message: str,
                        assistant_response: str, response_time: float,
                        sources_count: int = 0, intent: str = "unknown"):
    """Log a complete chat interaction.

    Args:
        session_id: Unique session identifier
        user_id: User identifier (can be IP, username, etc.)
        user_message: User's input message
        assistant_response: Assistant's response
        response_time: Time taken to generate response
        sources_count: Number of sources used
        intent: Detected user intent
    """
    # Sanitize messages for logging (remove newlines, limit length)
    user_msg_clean = user_message.replace('\n', ' ').strip()[:500]
    assistant_msg_clean = assistant_response.replace('\n', ' ').strip()[:1000]

    chat_logger.info(
        f"CHAT | Intent:{intent} | Sources:{sources_count} | Time:{response_time:.2f}s | "
        f"User:'{user_msg_clean}' | Assistant:'{assistant_msg_clean}'",
        extra={
            'session_id': session_id,
            'user_id': user_id
        }
    )


def log_session_event(session_id: str, user_id: str, event_type: str,
                     details: str = "", metadata: dict = None):
    """Log session-related events.

    Args:
        session_id: Unique session identifier
        user_id: User identifier
        event_type: Type of event (created, loaded, deleted, cleared, etc.)
        details: Additional details about the event
        metadata: Additional metadata as dictionary
    """
    metadata_str = f" | {metadata}" if metadata else ""
    chat_logger.info(
        f"SESSION | Event:{event_type} | Details:{details}{metadata_str}",
        extra={
            'session_id': session_id,
            'user_id': user_id
        }
    )


def log_user_activity(user_id: str, activity_type: str, details: str = "",
                     session_id: str = "unknown", metadata: dict = None):
    """Log general user activities.

    Args:
        user_id: User identifier
        activity_type: Type of activity (login, logout, settings_change, etc.)
        details: Activity details
        session_id: Associated session ID
        metadata: Additional metadata
    """
    metadata_str = f" | {metadata}" if metadata else ""
    chat_logger.info(
        f"USER | Activity:{activity_type} | Session:{session_id} | Details:{details}{metadata_str}",
        extra={
            'session_id': session_id,
            'user_id': user_id
        }
    )


def log_system_event(event_type: str, details: str, severity: str = "INFO",
                    metadata: dict = None):
    """Log system-level events.

    Args:
        event_type: Type of system event
        details: Event details
        severity: Severity level (INFO, WARNING, ERROR, CRITICAL)
        metadata: Additional metadata
    """
    metadata_str = f" | {metadata}" if metadata else ""
    message = f"SYSTEM | Event:{event_type} | {details}{metadata_str}"

    if severity == "WARNING":
        chat_logger.warning(message, extra={'session_id': 'system', 'user_id': 'system'})
    elif severity == "ERROR":
        chat_logger.error(message, extra={'session_id': 'system', 'user_id': 'system'})
    elif severity == "CRITICAL":
        chat_logger.critical(message, extra={'session_id': 'system', 'user_id': 'system'})
    else:
        chat_logger.info(message, extra={'session_id': 'system', 'user_id': 'system'})


def get_chat_logs_summary(days: int = 7) -> dict:
    """Get summary of chat logs for the specified number of days.

    Args:
        days: Number of days to look back

    Returns:
        Dictionary with log summary statistics
    """
    import datetime
    from collections import defaultdict

    chat_logs_dir = LOGS_DIR / "chat_sessions"
    if not chat_logs_dir.exists():
        return {"error": "Chat logs directory not found"}

    summary = {
        "total_sessions": set(),
        "total_users": set(),
        "total_interactions": 0,
        "avg_response_time": 0,
        "response_times": [],
        "intents": defaultdict(int),
        "daily_stats": defaultdict(int)
    }

    cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days)

    try:
        log_file = chat_logs_dir / "chat_sessions.log"
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                        
                    try:
                        # Parse log line - split by ' | ' and handle variable parts
                        parts = line.split(' | ')
                        if len(parts) >= 6:  # timestamp, level, session, user, type, details...
                            timestamp_str = parts[0]
                            level = parts[1]
                            session_info = parts[2]
                            user_info = parts[3]
                            message_type = parts[4]
                            details = ' | '.join(parts[5:])  # Rejoin remaining parts

                            # Parse timestamp
                            try:
                                timestamp = datetime.datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                                if timestamp < cutoff_date:
                                    continue
                            except:
                                continue

                            # Extract session and user IDs
                            if 'Session:' in session_info:
                                session_id = session_info.split('Session:')[1].strip()
                                summary["total_sessions"].add(session_id)

                            if 'User:' in user_info:
                                user_id = user_info.split('User:')[1].strip()
                                summary["total_users"].add(user_id)

                            # Parse different log types
                            if message_type == 'CHAT':
                                summary["total_interactions"] += 1

                                # Extract response time from details
                                if 'Time:' in details:
                                    time_part = details.split('Time:')[1].split('s')[0].strip()
                                    try:
                                        response_time = float(time_part)
                                        summary["response_times"].append(response_time)
                                    except:
                                        pass

                                # Extract intent from details
                                if 'Intent:' in details:
                                    intent_part = details.split('Intent:')[1].split(' | ')[0].strip()
                                    summary["intents"][intent_part] += 1

                            # Daily stats
                            day_key = timestamp.strftime('%Y-%m-%d')
                            summary["daily_stats"][day_key] += 1

                    except Exception as e:
                        # Skip malformed lines
                        continue

        # Calculate averages
        if summary["response_times"]:
            summary["avg_response_time"] = sum(summary["response_times"]) / len(summary["response_times"])

        # Convert sets to counts
        summary["total_sessions"] = len(summary["total_sessions"])
        summary["total_users"] = len(summary["total_users"])

        return dict(summary)

    except Exception as e:
        return {"error": f"Failed to parse logs: {str(e)}"}
