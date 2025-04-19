"""
Custom log formatters.

This module provides custom formatters for logging output.
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict

from app.logging.context import get_correlation_id, get_logging_context


class JSONFormatter(logging.Formatter):
    """Custom formatter that outputs logs in JSON format."""

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record as JSON."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "service": "aif-rag-api",
            "message": record.getMessage(),
        }

        # Add correlation ID from context
        log_data["correlation_id"] = get_correlation_id()

        # Add logging context
        log_data.update(get_logging_context())

        # Add all extra fields from record.__dict__
        for key, value in record.__dict__.items():
            if key not in ("args", "asctime", "created", "exc_info", "exc_text", 
                          "filename", "funcName", "id", "levelname", "levelno", 
                          "lineno", "module", "msecs", "message", "msg", "name", 
                          "pathname", "process", "processName", "relativeCreated", 
                          "stack_info", "thread", "threadName"):
                log_data[key] = value

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data) 