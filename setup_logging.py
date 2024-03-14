import os
from datetime import datetime
import pytz
import logging
import sys
import re

def setup_logging() -> str:
    # Setup data output and logging folders
    sydney_tz = pytz.timezone('Australia/Sydney')    
    sydney_datetime = datetime.now(sydney_tz)

    year: int = sydney_datetime.year
    month: int = sydney_datetime.month
    day: int = sydney_datetime.day

    folder_path: str = f'{year}/{month:02d}/{day:02d}'
    log_path: str = f'{folder_path}/log'
    bgg_list_path: str = f'{folder_path}/bgg_list'
    raw_path: str = f'{folder_path}/raw'

    os.makedirs(log_path, exist_ok=True)
    os.makedirs(bgg_list_path, exist_ok=True)
    os.makedirs(raw_path, exist_ok=True)
    
    python_file_name: str = sys.argv[0]
    pattern: str = "\w*(?=\.py)"
    python_file_name = re.search(pattern, python_file_name)[0]
    log_name: str = f"{python_file_name}.log"

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        filename=f'{log_path}/{log_name}',
                        filemode='a',
                        datefmt="%Y-%m-%d %H:%M:%S")
    
    logging.Formatter.converter = lambda *args: sydney_datetime.timetuple()
    logging.info(f'Running {__file__}')
    return folder_path, log_path, bgg_list_path, raw_path