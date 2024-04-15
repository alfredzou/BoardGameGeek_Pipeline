from default_repo.utils.bgg_utils import gcp_authenticate
from google.cloud import bigquery
import os

if 'custom' not in globals():
    from mage_ai.data_preparation.decorators import custom
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

def upload_dbt_docs_to_gcs(dbt_docs_path: str) -> None:
    local_file_list = [(f"{dbt_docs_path}/{file_name}", file_name) for file_name in os.listdir(dbt_docs_path)
                        if os.path.isfile(os.path.join(dbt_docs_path, file_name))]
    logging.info(f"{len(local_file_list)} found in {dbt_docs_path}")
    
    i=0
    for local_file, file_name in local_file_list:
        dbt_bucket.blob(file_name).upload_from_filename(local_file)
        if (i+1) % 10 == 0:
            logging.info(f"uploaded {i+1} files")
        i += 1
    logging.info(f"files uploaded from {dbt_docs_path}")
    return None

@custom
def main(*args, **kwargs) -> None:
    global logging
    logging = kwargs.get('logger')

    global dbt_bucket
    _, _, dbt_bucket = gcp_authenticate()
    logging.info(f"Google Cloud Platform authentication successful")

    dbt_docs_path = "/home/src/default_repo/dbt/bgg/target"
    upload_dbt_docs_to_gcs(dbt_docs_path)
    return None