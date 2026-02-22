"""
Robust Logging System for ACDICE
Architectural Choice: Using Loguru for structured logging with automatic rotation.
This provides better performance and features than standard logging module.
"""
import sys
from pathlib import Path
from typing import Dict, Any
from datetime import datetime
from loguru import logger
import json

class ACDCILogger:
    """Custom logger with structured logging and Firestore integration capability"""
    
    def __init__(self, config):
        self.config = config
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        self._setup_logger()
        
    def _setup_logger(self):
        """Configure logger with multiple sinks"""
        # Remove default handler
        logger.remove()
        
        # Console output with colors
        logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level=self.config.log_level,
            colorize=True
        )
        
        # File output with rotation
        log_file = self.log_dir / f"acdice_{datetime.now().strftime('%Y%m%d')}.log"
        logger.add(
            str(log_file),
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level="DEBUG",
            rotation="500 MB",
            retention=f"{self.config.log_retention_days} days",
            compression="zip",
            enqueue=True  # Thread-safe logging
        )
        
        # Error log for critical issues
        error_file = self.log_dir / "errors.log"
        logger.add(
            str(error_file),
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level="ERROR",
            rotation="100 MB",