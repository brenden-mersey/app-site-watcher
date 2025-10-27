"""
modules/logger.py
-----------------------
Logging configuration and setup.
"""

import logging

def initialize_logger(log_file_name):
    """
    Set up logging configuration with both console and file handlers.
    
    Args:
        log_file_name (str): Name of the log file to use
        
    Returns:
        logging.Logger: Configured logger instance
    """
    # Initialize basic logger for error messages during config loading
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]  # Start with console only
    )
    logger = logging.getLogger(__name__)

    # Reconfigure logging with file handler now that we have the log file name
    file_handler = logging.FileHandler(log_file_name)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)
    
    return logger

