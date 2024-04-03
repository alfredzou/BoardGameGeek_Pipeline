from requests.adapters import HTTPAdapter, Retry
import math
from time import sleep
from default_repo.utils.bgg_utils import folder_paths, gcp_authenticate
import requests
from requests.exceptions import ChunkedEncodingError

if 'custom' not in globals():
    from mage_ai.data_preparation.decorators import custom
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

def extract_id_list(id_path: str) -> list[str]:
    # Extract id list of bgg things
    with bucket.blob(id_path).open('r') as f:
        next(f)
        id_list: list = [row.rstrip() for row in f]
    
    logging.info(f"Extracted ids from bgg_id.csv: {len(id_list)} ids")
    return id_list

def prepare_api_call_dict(id_list: list[str]) -> dict[int:str]:
    ids_per_api_call: int = 900 # too many ids will trigger 414 URI too long
    id_count: int = len(id_list)
    api_call_count: int = math.ceil(id_count/ids_per_api_call)
    logging.info(f"{api_call_count} api calls to be made: {id_count} total ids with {ids_per_api_call} ids per api call")

    api_call_dict: dict[int:str] = {}
    for i in range(api_call_count):
        ids: list[str] = id_list[i*ids_per_api_call:(i+1)*ids_per_api_call]
        ids_string: str = ','.join(ids)
        api_call_dict[i] = ids_string

    return api_call_dict

def api_call(raw_data_path:str, api_call_dict:dict[int:str]) -> None:
    url = "https://boardgamegeek.com/xmlapi2/thing"
    local_temp_path = f"/home/src/default_repo/temp"

    logging.info(f'Creating session to connect with bgg api')
    with requests.Session() as s:
        retries = Retry(total=5, backoff_factor=2, status_forcelist=[429, 502, 503], allowed_methods=["GET"])
        s.mount('https://', HTTPAdapter(max_retries=retries))
        max_chunking_retries = 3
        api_wait = 10

        for i, api_ids_list in api_call_dict.items():
            params: dict = {"id":api_ids_list,"stats":"1","type":"boardgame,boardgameexpansion"}
            raw_file_path = f'{local_temp_path}/{raw_data_path}/{i}.xml'
            for retry_count in range(1, max_chunking_retries+1):
                try:
                    r = s.get(url, params=params)
                    r.raise_for_status()
                    
                    with open(raw_file_path, 'wb') as f:
                        for row in r:
                            f.write(row) 
                    break
                except ChunkedEncodingError as e:
                    logging.warning(f"An error occurred with api call {i}", exc_info=True)
                    if retry_count <= max_chunking_retries:
                        logging.warning(f"Retrying API call {i} after {api_wait} seconds...")
                        sleep(api_wait)
                    else:
                        logging.error(f"Maximum retry attempts reached for API call {i}", exc_info=True)
                        raise
                except Exception as e:
                    logging.error(f"An error occurred with api call {i}", exc_info=True)
                    raise

            if (i+1) % 10 == 0:
                logging.info(f"{i+1} api calls processed")

            sleep(api_wait)

    logging.info(f"api calls completed")   

    return None

@custom
def main(id_path, *args, **kwargs):
    global logging
    logging = kwargs.get('logger')

    global bucket
    bucket, _ = gcp_authenticate()
    logging.info(f"Google Cloud Platform authentication successful")

    _, _, raw_data_path, _, local_temp_path = folder_paths()
    id_list = extract_id_list(id_path)
    api_call_dict = prepare_api_call_dict(id_list)
    api_call(raw_data_path, api_call_dict)
    return None