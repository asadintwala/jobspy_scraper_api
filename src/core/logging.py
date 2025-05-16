''' importing modules'''
import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    '''Function to configure and initialize logging for the application'''
    # Set up basic configuration for logging
    logging.basicConfig(
        level=logging.INFO, # Set the logging level to INFO (you can change it to DEBUG, WARNING, etc.)
        # Define the format of log messages
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        # Define the handlers that determine where logs are output
        handlers=[
            # Write logs to a file 'jobscraper.log'
            # Rotate the log file after it reaches ~10MB
            # Keep up to 5 backup log files
            RotatingFileHandler(
                'jobscraper.log',
                maxBytes=10000000, # ~10 MB
                backupCount=5 # Keep last 5 log files
            ),
            # Also output log messages to the console (stdout)
            logging.StreamHandler()
        ]
    )
