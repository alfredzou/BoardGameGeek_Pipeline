import requests
import logging
from requests.adapters import HTTPAdapter, Retry
from setup_logging import setup_logging
import math
from time import sleep

def extract_id_list(bgg_list_path: str) -> list[str]:
    # Extract id list of bgg things
    id_path = f"{bgg_list_path}/bgg_id.csv"
    with open(id_path,'r') as f:
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

def api_call(raw_path:str, api_call_dict:dict[int:str]) -> None:
    url = "https://boardgamegeek.com/xmlapi2/thing"

    logging.info(f'Creating session to connect with bgg api')
    with requests.Session() as s:
        # retries = Retry(total=5, backoff_factor=2, status_forcelist=[429, 503], allowed_methods=["GET"])
        # s.mount('https://', HTTPAdapter(max_retries=retries))

        for i, api_ids_list in api_call_dict.items():
            params: dict = {"id":api_ids_list,"stats":"1"}
            raw_file_path = f'{raw_path}/{i}.xml'
            try:
                r = s.get(url, params=params)
                r.raise_for_status()
                
                with open(raw_file_path, 'wb') as f:
                    for row in r:
                        f.write(row) 
            except Exception as e:
                logging.error(f"An error occurred with api call {i}: {e}", exc_info=True)   

            if (i+1) % 10 == 0:
                logging.info(f"{i+1} api calls processed")

            sleep(10)

    logging.info(f"api calls completed")   

    return None

def main():
    _, _, bgg_list_path, raw_path = setup_logging()
    id_list = extract_id_list(bgg_list_path)
    api_call_dict = prepare_api_call_dict(id_list)
    api_call(raw_path, api_call_dict)

if __name__ == "__main__":
    main()
