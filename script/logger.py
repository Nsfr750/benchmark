"""
Logging module for the Benchmark application.
"""
import os
import logging
import atexit
from datetime import datetime
from pathlib import Path
from logging.handlers import RotatingFileHandler

# Create logs directory if it doesn't exist
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# Create a custom logger
logger = logging.getLogger("BenchmarkApp")
logger.setLevel(logging.DEBUG)

# Create handlers
log_file = LOG_DIR / f"benchmark_{datetime.now().strftime('%Y%m%d')}.log"

# Use RotatingFileHandler with 5MB max size and 5 backup files
file_handler = RotatingFileHandler(
    log_file,
    maxBytes=5*1024*1024,  # 5MB
    backupCount=5,
    encoding='utf-8',
    delay=False
)

console_handler = logging.StreamHandler()

# Set levels
file_handler.setLevel(logging.DEBUG)
console_handler.setLevel(logging.INFO)

# Create formatters and add it to handlers
log_format = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
file_handler.setFormatter(log_format)
console_handler.setFormatter(log_format)

# Add handlers to the logger
if not logger.handlers:  # Avoid adding handlers multiple times
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

def close_handlers():
    """Close all file handlers to release file handles."""
    for handler in logger.handlers[:]:
        if hasattr(handler, 'close'):
            handler.close()
        logger.removeHandler(handler)

# Register handler cleanup on exit
atexit.register(close_handlers)

def get_log_file_path():
    """Return the path to the current log file."""
    return str(log_file.absolute())

def clear_logs():
    """Clear all log files."""
    try:
        # Close all handlers first to release file handles
        close_handlers()
        
        # Delete log files
        deleted = 0
        for log_file_path in LOG_DIR.glob("*.log*"):  # Include rotated logs
            try:
                if log_file_path.is_file():
                    log_file_path.unlink()
                    deleted += 1
            except Exception as e:
                logger.error(f"Error deleting log file {log_file_path}: {e}")
        
        # Reinitialize handlers after cleanup
        if deleted > 0:
            logger.info(f"Cleared {deleted} log files")
            
    except Exception as e:
        logger.error(f"Error in clear_logs: {e}")
        return False
    finally:
        # Make sure we have working handlers
        if not logger.handlers:
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
        return True
