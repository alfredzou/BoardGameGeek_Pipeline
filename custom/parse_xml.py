from default_repo.utils.bgg_utils import folder_paths
import pyarrow as pa
import pyarrow.parquet as pq
from lxml import etree
import pandas as pd
from datetime import datetime
import pytz
import os
import math

if 'custom' not in globals():
    from mage_ai.data_preparation.decorators import custom
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test



@custom
def main(xml_batch, *args, **kwargs):
    global logging
    logging = kwargs.get('logger')
    batch_number = xml_batch[0]
    xml_batch_list = xml_batch[1]
    logging.info(f"processing batch number {batch_number}")

    _, _, _, stage_data_path, local_temp_path = folder_paths()
    sydney_date = get_date()
    
    return df_bgg_chunk, df_suggested_players_chunk