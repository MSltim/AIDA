"""
Centralized Logger Module with Color-Coded Output
Provides consistent logging across the entire application with visual distinction.
"""

import logging
import sys
from datetime import datetime
from enum import Enum
from typing import Optional


class LogColor(Enum):
    """ANSI color codes for terminal output"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    # Foreground colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright foreground colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'


class ColoredFormatter(logging.Formatter):
    """Custom formatter with color-coded output based on log level"""
    
    # Level-specific color mappings
    LEVEL_COLORS = {
        logging.DEBUG: LogColor.BRIGHT_BLACK.value,
        logging.INFO: LogColor.BRIGHT_CYAN.value,
        logging.WARNING: LogColor.BRIGHT_YELLOW.value,
        logging.ERROR: LogColor.BRIGHT_RED.value,
        logging.CRITICAL: f"{LogColor.BOLD.value}{LogColor.BG_RED.value}{LogColor.WHITE.value}"
    }
    
    # Component/module color
    MODULE_COLOR = LogColor.MAGENTA.value
    TIME_COLOR = LogColor.BRIGHT_BLACK.value
    MESSAGE_COLOR = LogColor.WHITE.value
    RESET = LogColor.RESET.value
    
    def __init__(self, fmt: Optional[str] = None, use_colors: bool = True):
        """
        Initialize the colored formatter.
        
        Args:
            fmt: Log format string (if None, uses default)
            use_colors: Whether to use colors (can be disabled for file logging)
        """
        super().__init__(fmt)
        self.use_colors = use_colors
    
    def format(self, record: logging.LogRecord) -> str:
        """Format the log record with colors"""
        if not self.use_colors:
            return super().format(record)
        
        # Get the color for this log level
        level_color = self.LEVEL_COLORS.get(record.levelno, self.MESSAGE_COLOR)
        
        # Format timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
        colored_timestamp = f"{self.TIME_COLOR}{timestamp}{self.RESET}"
        
        # Format level name with color
        colored_level = f"{level_color}{record.levelname:8s}{self.RESET}"
        
        # Format module/function name
        module_info = f"{record.name}"
        if record.funcName and record.funcName != '<module>':
            module_info = f"{record.name}.{record.funcName}"
        colored_module = f"{self.MODULE_COLOR}{module_info}{self.RESET}"
        
        # Format the message
        message = record.getMessage()
        
        # Special formatting for certain patterns
        if "---" in message:  # Workflow events
            message = f"{LogColor.BRIGHT_BLUE.value}{message}{self.RESET}"
        elif "ERROR" in message.upper() or "FAILED" in message.upper():
            message = f"{LogColor.BRIGHT_RED.value}{message}{self.RESET}"
        elif "SUCCESS" in message.upper() or "COMPLETE" in message.upper():
            message = f"{LogColor.BRIGHT_GREEN.value}{message}{self.RESET}"
        elif "WARN" in message.upper():
            message = f"{LogColor.BRIGHT_YELLOW.value}{message}{self.RESET}"
        else:
            message = f"{self.MESSAGE_COLOR}{message}{self.RESET}"
        
        # Combine all parts
        formatted = f"{colored_timestamp} | {colored_level} | {colored_module} | {message}"
        
        # Add exception info if present
        if record.exc_info:
            formatted += f"\n{self.formatException(record.exc_info)}"
        
        return formatted


class AppLogger:
    """Centralized Logger for the entire application"""
    
    _instance = None
    _loggers = {}
    
    def __new__(cls):
        """Singleton pattern to ensure only one logger instance"""
        if cls._instance is None:
            cls._instance = super(AppLogger, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the logger (only once)"""
        if self._initialized:
            return
        
        self._initialized = True
        self._default_level = logging.INFO
        self._setup_root_logger()
    
    def _setup_root_logger(self):
        """Set up the root logger configuration"""
        import os
        root_logger = logging.getLogger()
        root_logger.setLevel(self._default_level)
        
        # Remove existing handlers to avoid duplicates
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Check if colors should be disabled (e.g., for MCP servers)
        disable_colors = os.environ.get('DISABLE_AIDA_COLORS', '').lower() in ('1', 'true', 'yes')
        
        # Console handler - use colors only if not disabled
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(self._default_level)
        console_handler.setFormatter(ColoredFormatter(use_colors=not disable_colors))
        root_logger.addHandler(console_handler)
    
    def get_logger(self, name: str, level: Optional[int] = None) -> logging.Logger:
        """
        Get or create a logger for a specific module.
        
        Args:
            name: Name of the logger (typically __name__ from the calling module)
            level: Optional log level override for this specific logger
        
        Returns:
            A configured logger instance
        """
        if name in self._loggers:
            return self._loggers[name]
        
        logger = logging.getLogger(name)
        
        if level is not None:
            logger.setLevel(level)
        
        self._loggers[name] = logger
        return logger
    
    def set_level(self, level: int, logger_name: Optional[str] = None):
        """
        Set the log level globally or for a specific logger.
        
        Args:
            level: The logging level (e.g., logging.DEBUG, logging.INFO)
            logger_name: Optional specific logger name, if None affects all loggers
        """
        if logger_name:
            if logger_name in self._loggers:
                self._loggers[logger_name].setLevel(level)
        else:
            self._default_level = level
            logging.getLogger().setLevel(level)
            for logger in self._loggers.values():
                logger.setLevel(level)
    
    def add_file_handler(self, filepath: str, level: Optional[int] = None, use_colors: bool = False):
        """
        Add a file handler to log to a file.
        
        Args:
            filepath: Path to the log file
            level: Optional log level for file output
            use_colors: Whether to include color codes in file (usually False)
        """
        # Create directory if it doesn't exist
        import os
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        file_handler = logging.FileHandler(filepath, mode='a', encoding='utf-8')
        file_handler.setLevel(level or self._default_level)
        
        # Use standard logging format for files (no colors)
        if use_colors:
            file_handler.setFormatter(ColoredFormatter(use_colors=True))
        else:
            # Standard format without colors for files
            file_formatter = logging.Formatter(
                fmt='%(asctime)s | %(levelname)-8s | %(name)s.%(funcName)s | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_formatter)
        
        root_logger = logging.getLogger()
        root_logger.addHandler(file_handler)
    
    def disable_colors(self):
        """Disable color output (useful for environments that don't support ANSI)"""
        root_logger = logging.getLogger()
        for handler in root_logger.handlers:
            if isinstance(handler, logging.StreamHandler):
                handler.setFormatter(ColoredFormatter(use_colors=False))


# Global logger instance
_app_logger = AppLogger()


def get_logger(name: str = __name__, level: Optional[int] = None) -> logging.Logger:
    """
    Convenience function to get a logger.
    
    Usage:
        from utils.logger import get_logger
        logger = get_logger(__name__)
        logger.info("This is an info message")
        logger.error("This is an error message")
    
    Args:
        name: Name of the logger (use __name__ in most cases)
        level: Optional log level override
    
    Returns:
        A configured logger instance
    """
    return _app_logger.get_logger(name, level)


def set_log_level(level: int, logger_name: Optional[str] = None):
    """
    Set the log level globally or for a specific logger.
    
    Usage:
        from utils.logger import set_log_level
        import logging
        set_log_level(logging.DEBUG)  # Enable debug logging globally
    
    Args:
        level: The logging level (e.g., logging.DEBUG, logging.INFO)
        logger_name: Optional specific logger name
    """
    _app_logger.set_level(level, logger_name)


def add_file_logging(filepath: str, level: Optional[int] = None):
    """
    Add file logging to the application.
    
    Usage:
        from utils.logger import add_file_logging
        add_file_logging('logs/app.log')
    
    Args:
        filepath: Path to the log file
        level: Optional log level for file output
    """
    _app_logger.add_file_handler(filepath, level, use_colors=False)


def add_session_file_logging(session_folder: str, session_id: str, level: Optional[int] = None):
    """
    Add session-specific file logging to a dedicated logs folder within the session.
    
    Creates a logs/ subfolder in the session directory and writes all logs there.
    
    Usage:
        from utils.logger import add_session_file_logging
        add_session_file_logging('/path/to/session_folder', 'session_20251013_143000')
    
    Args:
        session_folder: Path to the session folder
        session_id: Session identifier for the log filename
        level: Optional log level for file output
    """
    import os
    
    # Create logs subfolder in session directory
    logs_folder = os.path.join(session_folder, 'logs')
    os.makedirs(logs_folder, exist_ok=True)
    
    # Create log file with session ID
    log_filepath = os.path.join(logs_folder, f'{session_id}.log')
    
    # Ensure the file is created and writable
    try:
        # Create empty file if it doesn't exist
        with open(log_filepath, 'a', encoding='utf-8') as f:
            f.write(f"=== Session Log Started: {session_id} ===\n")
    except Exception as e:
        print(f"WARNING: Could not create log file: {e}")
        return None
    
    # Add the file handler to root logger
    _app_logger.add_file_handler(log_filepath, level or logging.INFO, use_colors=False)
    
    # Log the initialization (this should now go to both console and file)
    logger = get_logger('session_logger')
    logger.info(f"[LOG] Session logging initialized: {log_filepath}")
    logger.info(f"[LOG] Log file location: {os.path.abspath(log_filepath)}")
    
    return log_filepath


def disable_color_logging():
    """
    Disable color output in logs.
    
    Usage:
        from utils.logger import disable_color_logging
        disable_color_logging()
    """
    _app_logger.disable_colors()
