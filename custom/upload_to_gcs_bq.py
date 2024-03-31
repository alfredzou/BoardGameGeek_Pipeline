from default_repo.utils.bgg_utils import folder_paths, gcp_authenticate, get_date
import os
from google.cloud import bigquery
import pandas as pd

if 'custom' not in globals():
    from mage_ai.data_preparation.decorators import custom
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

def upload_to_gcs(local_temp_path: str, path: str) -> None:
    local_path = f"{local_temp_path}/{path}"
    local_file_list = [(f"{local_path}/{file_name}", file_name) for file_name in os.listdir(f"{local_path}")]
    logging.info(f"{len(local_file_list)} found in {local_path}")
    
    i=0
    for local_file, file_name in local_file_list:
        bucket.blob(f"{path}/{file_name}").upload_from_filename(local_file)
        if (i+1) % 10 == 0:
            logging.info(f"uploaded {i+1} files to {path}")
        i += 1
    logging.info(f"files uploaded from {local_path} to {path}")
    return None

def read_pq_files(local_temp_path: str, path: str, mode: str) -> None:
    local_path = f"{local_temp_path}/{path}"
    local_file_list = [(f"{local_path}/{file_name}", file_name)
                        for file_name in os.listdir(f"{local_path}")
                        if file_name.startswith(mode)]
    logging.info(f"{len(local_file_list)} {mode} files found in {local_path}")

    df = pd.DataFrame()
    for file_path, _ in local_file_list:
        df_chunk = pd.read_parquet(file_path)
        df = pd.concat([df,df_chunk], axis = 0)
    logging.info(f"{mode} df created")
    return df

def create_bq_table(schema:str) -> None:
    try:
        dataset = bq_client.create_dataset(schema)  
        logging.info("{schema} created")
    except Exception as e:
        logging.info("{schema} already exists. Skipping...")
        pass
    return None

def upload_to_bq(local_temp_path:str, stage_data_path:str , schema:str, sydney_date) -> None:
    bgg_df = read_pq_files(local_temp_path, stage_data_path,'bgg')
    sp_df = read_pq_files(local_temp_path, stage_data_path,'sp')

    create_bq_table(schema)

    bgg_table_name = f'bgg-{sydney_date}'
    sp_table_name = f'sp-{sydney_date}'

    bgg_table_ref = bq_client.dataset(schema).table(bgg_table_name)
    sp_table_ref = bq_client.dataset(schema).table(sp_table_name)

    job_config = bigquery.LoadJobConfig(write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE)

    bgg_job = bq_client.load_table_from_dataframe(bgg_df, bgg_table_ref, job_config=job_config)
    logging.info(f"bgg_df uploaded to {bgg_table_name}")

    sp_job = bq_client.load_table_from_dataframe(sp_df, sp_table_ref, job_config=job_config)
    logging.info(f"sp_df uploaded to {sp_table_name}")
    return None

@custom
def main(*args, **kwargs):
    global logging
    logging = kwargs.get('logger')

    global bucket
    bucket, bq_credentials = gcp_authenticate()
    logging.info(f"Google Cloud Platform authentication successful")

    global bq_client
    bq_client = bigquery.Client(credentials=bq_credentials)
    logging.info(f"BigQuery authentication successful")

    _, _, _, stage_data_path, local_temp_path = folder_paths()
    schema="bgg_stage"
    sydney_date = get_date()
    upload_to_gcs(local_temp_path, stage_data_path)
    upload_to_bq(local_temp_path, stage_data_path, schema, sydney_date)
    return None