''' importing modules'''
import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    '''defining logging function'''
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            RotatingFileHandler(
                'jobscraper.log',
                maxBytes=10000000,
                backupCount=5
            ),
            logging.StreamHandler()
        ]
    )
    