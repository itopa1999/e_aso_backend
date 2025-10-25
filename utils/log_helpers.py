import logging
import time
import traceback
from datetime import datetime

# logger = logging.getLogger("project")
logger = logging.getLogger(__name__)


class OperationLogger:
    """Utility class for structured operation logging with timestamps."""

    def __init__(self, command_name: str, **kwargs):
        self.command_name = command_name
        self.kwargs = kwargs
        self.start_time = None

    def _timestamp(self):
        """Return formatted timestamp."""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def start(self):
        """Mark the start of an operation."""
        self.start_time = time.time()
        lines = [
            "----------------------------------------------",
            f"[{self._timestamp()}] [INFO] [{self.command_name}] Starting operation...",
        ]
        for key, val in self.kwargs.items():
            lines.append(f"| {key.capitalize():<12}: {val}")
        lines.append("| Status       : In Progress")
        lines.append("----------------------------------------------")
        logger.info("\n" + "\n".join(lines))

    def success(self, message: str = "Completed successfully"):
        """Log success with timing."""
        duration = time.time() - self.start_time if self.start_time else 0
        logger.info(
            f"[{self._timestamp()}] [INFO] [{self.command_name}] {message} "
            f"in {duration:.2f}s"
        )

    def fail(self, message: str = "Operation failed", exc: Exception = None):
        """Log failure with timing and optional traceback."""
        duration = time.time() - self.start_time if self.start_time else 0
        logger.error(
            f"[{self._timestamp()}] [ERROR] [{self.command_name}] {message} "
            f"after {duration:.2f}s"
        )
        if exc:
            logger.debug(traceback.format_exc())
