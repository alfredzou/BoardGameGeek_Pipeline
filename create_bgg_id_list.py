import requests
from bs4 import BeautifulSoup
import json
import logging
import os
from datetime import datetime
import pytz
from requests.adapters import HTTPAdapter, Retry
import zipfile
import io
import csv

def create_id_list(bgg_list_path, csv_path) -> None:
    # Create id list of bgg things
    ids = []
    with open(csv_path,'r',newline='') as f:
        csvreader = csv.reader(f)
        for row in csvreader:
            first_column_value = row[0]
            ids.append(first_column_value)
    
    logging.info(f"Extracted {len(ids)-1} ids")

    id_path = f"{bgg_list_path}/bgg_id.csv"
    with open(id_path,'w') as f:
        for id in ids:
            f.write(f"{id}\n")
    
    logging.info("Created bgg_id.csv")

    return None

def download_bgg_list(bgg_list_path, session) -> str:
    # Locate download link in page, the link changes daily
    r = session.get("https://boardgamegeek.com/data_dumps/bg_ranks")
    soup = BeautifulSoup(r.text, 'html.parser')
    zip_url = soup.find('a',string="Click to Download")['href']

    r = requests.get(zip_url)
    file_name = "boardgames_ranks.csv"

    if r.status_code == 200:
        with io.BytesIO(r.content) as zip_buffer:
            with zipfile.ZipFile(zip_buffer, 'r') as zip_ref:
                zip_ref.extractall(f"{bgg_list_path}")
            logging.info(f"{file_name} downloaded successfully.")
    else:
        logging.error(f"{file_name} failed to download: {r.status_code=}")

    csv_path = f"{bgg_list_path}/{file_name}"
    return csv_path

def login_bgg(bgg_list_path) -> str:
    '''
    To limit the number of API calls download the boardgame_ranks.csv, an id list of boardgame things (boardgames, expansions, etc.).
    This file is updated daily. To access file, must be logged in.
    '''
    with requests.Session() as s:
        logging.info(f'Creating login session to BoardGameGeek')
        retries = Retry(total=2, backoff_factor=2, status_forcelist=[400], allowed_methods=["POST"])
        s.mount('https://', HTTPAdapter(max_retries=retries))
        
        body=json.dumps({"credentials": {"username": "apidummy", "password": "apidummy"}})
        headers={
        'authority': 'boardgamegeek.com',
        'content-type': 'application/json',
        'origin': 'https://boardgamegeek.com',
        'referer': 'https://boardgamegeek.com/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        }

        try:
            p = s.post('https://boardgamegeek.com/login/api/v1', data=body, headers=headers)
            logging.info(f"Login successful with status code {p.status_code}")
        except Exception as e:
            logging.error(f"An error occurred: {e}", exc_info=True)
        
        csv_path = download_bgg_list(bgg_list_path, session=s)
    return csv_path

def setup() -> str:
    # Setup data output and logging folders
    sydney_tz = pytz.timezone('Australia/Sydney')    
    sydney_datetime = datetime.now(sydney_tz)

    year: int = sydney_datetime.year
    month: int = sydney_datetime.month
    day: int = sydney_datetime.day

    folder_path: str = f'{year}/{month:02d}/{day:02d}'
    log_path: str = f'{folder_path}/log'
    bgg_list_path: str = f'{folder_path}/bgg_list'

    os.makedirs(log_path, exist_ok=True)
    os.makedirs(bgg_list_path, exist_ok=True)

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        filename=f'{log_path}/create_bgg_id_list.log',
                        filemode='a',
                        datefmt="%Y-%m-%d %H:%M:%S")
    
    logging.Formatter.converter = lambda *args: sydney_datetime.timetuple()
    logging.info(f'Running {__file__}')
    return bgg_list_path 

def main():
    bgg_list_path = setup()
    csv_path = login_bgg(bgg_list_path)
    create_id_list(bgg_list_path, csv_path)

if __name__ == "__main__":
    main()
