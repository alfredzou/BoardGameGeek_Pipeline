import requests
from requests.adapters import HTTPAdapter, Retry
import json
from bs4 import BeautifulSoup
import zipfile
import csv
import io
from default_repo.utils.setup_folders import setup_folders

if 'custom' not in globals():
    from mage_ai.data_preparation.decorators import custom
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


def create_id_list(bgg_list_path: str, csv_path: str) -> None:
    # Create id list of bgg things
    with open(csv_path,'r',newline='') as f:
        csvreader = csv.reader(f)
        ids: list[str] = [row[0] for row in csvreader]

    logging.info(f"Extracted {len(ids)-1} ids")
    
    id_path: str = f"{bgg_list_path}/bgg_id.csv"
    with open(id_path,'w') as f:
        for id in ids:
            f.write(f"{id}\n")
    
    logging.info(f"Created bgg_id.csv at {id_path}")

    return None

def download_bgg_list(bgg_list_path: str, session) -> str:
    # Locate download link in page, the link changes daily
    r = session.get("https://boardgamegeek.com/data_dumps/bg_ranks")
    soup = BeautifulSoup(r.text, 'html.parser')
    zip_url = soup.find('a',string="Click to Download")['href']

    try:
        r = requests.get(zip_url)
        r.raise_for_status()

        file_name = "boardgames_ranks.csv"     
        with io.BytesIO(r.content) as zip_buffer:
            with zipfile.ZipFile(zip_buffer, 'r') as zip_ref:
                zip_ref.extractall(f"{bgg_list_path}")
        logging.info(f"{file_name} downloaded successfully.")

    except Exception as e:
        logging.error(f"{file_name} failed to download: {e}", exc_info=True)

    csv_path = f"{bgg_list_path}/{file_name}"
    return csv_path

def login_bgg(bgg_list_path: str) -> str:
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
            p.raise_for_status()
            logging.info(f"Login successful with status code {p.status_code}")
        except Exception as e:
            logging.error(f"An error occurred: {e}", exc_info=True)

        csv_path = download_bgg_list(bgg_list_path, session=s)
    return csv_path

@custom
def main(*args, **kwargs):
    global logging
    logging = kwargs.get('logger')
    _, bgg_list_path, _ = setup_folders()
    csv_path = login_bgg(bgg_list_path)
    create_id_list(bgg_list_path, csv_path)
    return None