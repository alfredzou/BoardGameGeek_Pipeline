import os
from datetime import datetime
import pytz

def setup_folders(**kwargs) -> str:
    # Setup data output and logging folders
    sydney_tz = pytz.timezone('Australia/Sydney')    
    sydney_datetime = datetime.now(sydney_tz)

    year: int = sydney_datetime.year
    month: int = sydney_datetime.month
    day: int = sydney_datetime.day

    folder_path: str = f'/home/src/default_repo/{year}/{month:02d}/{day:02d}'
    bgg_list_path: str = f'{folder_path}/bgg_list'
    raw_path: str = f'{folder_path}/raw'

    os.makedirs(bgg_list_path, exist_ok=True)
    os.makedirs(raw_path, exist_ok=True)

    return folder_path, bgg_list_path, raw_path