from default_repo.utils.bgg_utils import gcp_authenticate
from google.cloud import bigquery

if 'custom' not in globals():
    from mage_ai.data_preparation.decorators import custom
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

def upload_dbt_docs_to_gcs(dbt_docs_path: str) -> None:
    dbt_doc_files = ['catalog.json',
                    'graph.gpickle',
                    'graph_summary.json',
                    'index.html',
                    'manifest.json',
                    'partial_parse.msgpack',
                    'run_results.json',
                    'semantic_manifest.json'
                    ]
    local_path = f"{dbt_docs_path}"
    local_file_list = [(f"{local_path}/{file_name}", file_name) for file_name in dbt_doc_files]
    logging.info(f"{len(local_file_list)} found in {local_path}")
    
    i=0
    for local_file, file_name in local_file_list:
        dbt_bucket.blob(file_name).upload_from_filename(local_file)
        if (i+1) % 10 == 0:
            logging.info(f"uploaded {i+1} files")
        i += 1
    logging.info(f"files uploaded from {local_path}")
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