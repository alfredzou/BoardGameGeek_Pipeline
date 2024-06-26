import os
from datetime import datetime
import pytz
import json
from google.cloud import storage
from google.oauth2 import service_account

def get_date() -> datetime:
    sydney_tz = pytz.timezone('Australia/Sydney')    
    sydney_datetime = datetime.now(sydney_tz)
    sydney_date = sydney_datetime.date()
    return sydney_date

def gcp_authenticate():
    with open(os.getenv('path_to_keyfile'), 'r') as f:
        info = json.load(f)

    credentials = service_account.Credentials.from_service_account_info(info)
    storage_client = storage.Client(credentials=credentials)
    
    mage_bucket = storage_client.bucket(os.getenv('GCS_BUCKET_NAME'))
    dbt_bucket = storage_client.bucket(os.getenv('DBT_GCS_BUCKET_NAME'))

    return mage_bucket, credentials, dbt_bucket

def folder_paths() -> str:
    # Setup data output and logging folders
    sydney_tz = pytz.timezone('Australia/Sydney')    
    sydney_datetime = datetime.now(sydney_tz)

    year: int = sydney_datetime.year
    month: int = sydney_datetime.month
    day: int = sydney_datetime.day

    folder_path: str = f'{year}/{month:02d}/{day:02d}'
    bgg_list_path: str = f'{folder_path}/bgg_list'
    raw_data_path: str = f'{folder_path}/raw_data'
    stage_data_path: str = f'{folder_path}/stage_data'
    local_temp_path: str = f'/home/src/default_repo/temp'

    return folder_path, bgg_list_path, raw_data_path, stage_data_path, local_temp_path