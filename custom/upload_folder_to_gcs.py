from default_repo.utils.bgg_utils import folder_paths, gcp_authenticate
import os

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
    logging.info(f"files uploaded {local_path}")
    return None

@custom
def main(*args, **kwargs):
    global logging
    logging = kwargs.get('logger')

    global bucket
    bucket, _ = gcp_authenticate()
    logging.info(f"Google Cloud Platform authentication successful")

    _, _, raw_data_path, _, local_temp_path = folder_paths()
    upload_to_gcs(local_temp_path, raw_data_path)
    return None