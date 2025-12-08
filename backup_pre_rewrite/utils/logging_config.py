"""
CENTRALIZED LOGGING MODULE
==========================
Professional logging system for the Atlas Financial Intelligence engine.

Features:
- Rotating file logs (prevents disk space issues)
- Multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Structured logging with timestamps
- Automatic log rotation (10MB max per file, 5 backup files)
- Console and file output
- Security event logging
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional
import warnings
warnings.filterwarnings('ignore')


class EngineLogger:
    """
    Centralized logging for Atlas Financial Intelligence.
    Provides structured, rotating logs with security event tracking.
    """
    
    _loggers = {}  # Cache for loggers
    
    @staticmethod
    def setup_logger(
        name: str = "AtlasEngine",
        log_level: str = "INFO",
        log_to_file: bool = True,
        log_to_console: bool = True,
        log_dir: str = "logs"
    ) -> logging.Logger:
        """
        Set up a logger with both file and console handlers.
        
        Args:
            name: Logger name (usually module name)
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_to_file: Enable file logging
            log_to_console: Enable console logging
            log_dir: Directory for log files
            
        Returns:
            Configured logger instance
        """
        # Return cached logger if already exists
        if name in EngineLogger._loggers:
            return EngineLogger._loggers[name]
        
        # Create logger
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
        
        # Prevent duplicate handlers
        if logger.hasHandlers():
            logger.handlers.clear()
        
        # Create formatter
        formatter = logging.Formatter(
            fmt='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # File handler (rotating)
        if log_to_file:
            # Create log directory if it doesn't exist
            log_path = Path(log_dir)
            log_path.mkdir(parents=True, exist_ok=True)
            
            # Rotating file handler (10MB max, 5 backup files)
            log_file = log_path / f"{name.lower()}.log"
            file_handler = RotatingFileHandler(
                filename=log_file,
                maxBytes=10 * 1024 * 1024,  # 10 MB
                backupCount=5,
                encoding='utf-8'
            )
            file_handler.setLevel(logging.DEBUG)  # Log everything to file
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        # Console handler
        if log_to_console:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.WARNING)  # Only warnings+ to console
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        # Cache logger
        EngineLogger._loggers[name] = logger
        
        return logger
    
    @staticmethod
    def get_logger(name: str = "AtlasEngine") -> logging.Logger:
        """
        Get existing logger or create a new one.
        
        Args:
            name: Logger name
            
        Returns:
            Logger instance
        """
        if name in EngineLogger._loggers:
            return EngineLogger._loggers[name]
        return EngineLogger.setup_logger(name)
    
    @staticmethod
    def log_security_event(event_type: str, details: str, severity: str = "WARNING"):
        """
        Log security-related events (attacks, validation failures, etc.).
        
        Args:
            event_type: Type of security event (e.g., "SQL_INJECTION", "XSS_ATTEMPT")
            details: Event details
            severity: Log severity (WARNING, ERROR, CRITICAL)
        """
        logger = EngineLogger.get_logger("SecurityLog")
        log_method = getattr(logger, severity.lower(), logger.warning)
        log_method(f"[{event_type}] {details}")
    
    @staticmethod
    def log_data_extraction(ticker: str, success: bool, error: Optional[str] = None):
        """
        Log data extraction events.
        
        Args:
            ticker: Stock ticker
            success: Whether extraction succeeded
            error: Error message if failed
        """
        logger = EngineLogger.get_logger("DataExtraction")
        if success:
            logger.info(f"Successfully extracted data for {ticker}")
        else:
            logger.error(f"Failed to extract data for {ticker}: {error}")
    
    @staticmethod
    def log_ai_request(model: str, prompt_length: int, response_length: int, success: bool):
        """
        Log AI model requests.
        
        Args:
            model: AI model name
            prompt_length: Length of prompt
            response_length: Length of response
            success: Whether request succeeded
        """
        logger = EngineLogger.get_logger("AIService")
        status = "SUCCESS" if success else "FAILED"
        logger.info(f"AI Request [{model}] {status} | Prompt: {prompt_length} chars | Response: {response_length} chars")
    
    @staticmethod
    def log_user_action(action: str, details: Optional[str] = None):
        """
        Log user actions (for analytics and debugging).
        
        Args:
            action: Action name (e.g., "EXTRACT_DATA", "EXPORT_PDF")
            details: Additional details
        """
        logger = EngineLogger.get_logger("UserActions")
        message = f"User Action: {action}"
        if details:
            message += f" | {details}"
        logger.info(message)


# ==========================================
# HELPER FUNCTIONS
# ==========================================

def get_logger(name: str = "AtlasEngine") -> logging.Logger:
    """
    Quick helper to get a logger.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    return EngineLogger.get_logger(name)


def log_error(message: str, exception: Optional[Exception] = None, logger_name: str = "AtlasEngine"):
    """
    Quick helper to log an error.
    
    Args:
        message: Error message
        exception: Exception object (optional)
        logger_name: Logger name
    """
    logger = EngineLogger.get_logger(logger_name)
    if exception:
        logger.error(f"{message}: {str(exception)}", exc_info=True)
    else:
        logger.error(message)


def log_warning(message: str, logger_name: str = "AtlasEngine"):
    """
    Quick helper to log a warning.
    
    Args:
        message: Warning message
        logger_name: Logger name
    """
    logger = EngineLogger.get_logger(logger_name)
    logger.warning(message)


def log_info(message: str, logger_name: str = "AtlasEngine"):
    """
    Quick helper to log an info message.
    
    Args:
        message: Info message
        logger_name: Logger name
    """
    logger = EngineLogger.get_logger(logger_name)
    logger.info(message)


if __name__ == "__main__":
    # Test the logging system
    print("=" * 80)
    print("TESTING LOGGING SYSTEM")
    print("=" * 80)
    
    # Set up logger
    logger = EngineLogger.setup_logger("TestLogger", log_level="DEBUG")
    
    # Test different log levels
    logger.debug("This is a DEBUG message (file only)")
    logger.info("This is an INFO message (file only)")
    logger.warning("This is a WARNING message (console + file)")
    logger.error("This is an ERROR message (console + file)")
    logger.critical("This is a CRITICAL message (console + file)")
    
    # Test security logging
    EngineLogger.log_security_event("SQL_INJECTION", "Detected SQL pattern in ticker: '; DROP TABLE", "ERROR")
    
    # Test data extraction logging
    EngineLogger.log_data_extraction("AAPL", success=True)
    EngineLogger.log_data_extraction("INVALID", success=False, error="Ticker not found")
    
    # Test AI logging
    EngineLogger.log_ai_request("gemini-2.0-flash-exp", 150, 500, success=True)
    
    # Test user action logging
    EngineLogger.log_user_action("EXTRACT_DATA", "ticker=AAPL")
    
    print("\n" + "=" * 80)
    print("Check the 'logs/' directory for log files!")
    print("=" * 80)


