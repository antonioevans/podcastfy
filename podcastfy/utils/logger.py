"""
Logger Module

This module provides a utility function to set up and configure a logger for the Podcastfy application.
It ensures consistent logging format and configuration across the application.
"""

import os
import logging
from typing import Optional, Dict, Any
from podcastfy.utils.config import load_config

def setup_logger(name: str) -> logging.Logger:
    """
    Set up and configure a logger.

    Args:
        name (str): The name of the logger.

    Returns:
        logging.Logger: A configured logger instance.
    """
    # Create logger
    logger = logging.getLogger(name)
    
    # Remove any existing handlers
    if logger.handlers:
        logger.handlers.clear()
    
    try:
        # Load config
        config = load_config()
        logging_config = config.get('logging', {
            'level': 'INFO',
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        })
        
        # Set log level
        level = logging_config.get('level', 'INFO')
        if isinstance(level, str):
            numeric_level = getattr(logging, level.upper(), logging.INFO)
        else:
            numeric_level = logging.INFO
        logger.setLevel(numeric_level)
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(numeric_level)
        
        # Create formatter
        log_format = logging_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        formatter = logging.Formatter(log_format)
        console_handler.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(console_handler)
        
        # Optionally set up file handler if log file path is specified
        log_file = logging_config.get('file')
        if log_file:
            # Ensure log directory exists
            log_dir = os.path.dirname(log_file)
            if log_dir:
                os.makedirs(log_dir, exist_ok=True)
                
            # Create file handler
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(numeric_level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        return logger
        
    except Exception as e:
        # Fallback to basic configuration if there's an error
        fallback_logger = logging.getLogger(name)
        if fallback_logger.handlers:
            fallback_logger.handlers.clear()
            
        console_handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        fallback_logger.addHandler(console_handler)
        fallback_logger.setLevel(logging.INFO)
        
        fallback_logger.warning(f"Error setting up logger with config, using fallback configuration: {str(e)}")
        return fallback_logger

def main():
    """Test the logger setup."""
    try:
        # Test basic logger
        logger = setup_logger(__name__)
        logger.debug("This is a debug message")
        logger.info("This is an info message")
        logger.warning("This is a warning message")
        logger.error("This is an error message")
        
        # Test logger with different levels
        levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        for level in levels:
            test_logger = setup_logger(f"test_logger_{level}")
            test_logger.setLevel(level)
            test_logger.debug("Debug test")
            test_logger.info("Info test")
            test_logger.warning("Warning test")
            test_logger.error("Error test")
            test_logger.critical("Critical test")
            
    except Exception as e:
        print(f"Error testing logger: {str(e)}")
        raise

if __name__ == "__main__":
    main()
