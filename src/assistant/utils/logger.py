"""
Logger setup and utilities
"""
import logging
import sys
from pathlib import Path
from datetime import datetime
from logging.handlers import RotatingFileHandler
import os


def get_log_dir() -> Path:
    """Get the log directory path"""
    if os.name == 'nt':
        log_dir = Path(os.environ.get('APPDATA', Path.home())) / 'MyAssistant' / 'logs'
    else:
        log_dir = Path.home() / '.myassistant' / 'logs'
    
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


class ColorFormatter(logging.Formatter):
    """Colored log formatter for console output"""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[41m', # Red background
    }
    RESET = '\033[0m'
    
    def format(self, record):
        color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)


def setup_logging(level: int = logging.INFO, log_to_file: bool = True) -> None:
    """Setup application logging"""
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_formatter = ColorFormatter(
        '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler with rotation
    if log_to_file:
        log_dir = get_log_dir()
        log_file = log_dir / f'assistant_{datetime.now().strftime("%Y%m%d")}.log'
        
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)-30s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
    
    # Reduce noise from third-party libraries
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('PIL').setLevel(logging.WARNING)


class ContextLogger:
    """Logger that includes context information"""
    
    def __init__(self, name: str, context: dict = None):
        self.logger = logging.getLogger(name)
        self.context = context or {}
    
    def _format_message(self, msg: str) -> str:
        if self.context:
            ctx_str = ' | '.join(f'{k}={v}' for k, v in self.context.items())
            return f"[{ctx_str}] {msg}"
        return msg
    
    def debug(self, msg: str, *args, **kwargs):
        self.logger.debug(self._format_message(msg), *args, **kwargs)
    
    def info(self, msg: str, *args, **kwargs):
        self.logger.info(self._format_message(msg), *args, **kwargs)
    
    def warning(self, msg: str, *args, **kwargs):
        self.logger.warning(self._format_message(msg), *args, **kwargs)
    
    def error(self, msg: str, *args, **kwargs):
        self.logger.error(self._format_message(msg), *args, **kwargs)
    
    def critical(self, msg: str, *args, **kwargs):
        self.logger.critical(self._format_message(msg), *args, **kwargs)
