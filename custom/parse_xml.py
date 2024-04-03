from default_repo.utils.bgg_utils import folder_paths, get_date
import pyarrow as pa
import pyarrow.parquet as pq
from lxml import etree
import pandas as pd
import os
import math

if 'custom' not in globals():
    from mage_ai.data_preparation.decorators import custom
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

def list_to_string(my_list: list[str]) -> str:
	if len(my_list) == 0:
		return pd.NA
	else:
		string = '|,|'.join(my_list)
		return string

def parse_xml(doc, sydney_date, xml_path: str):
    bgg_list: list[list[str]] = []
    suggested_players_list: list[list[str]] = []
    for item in doc.xpath('/items/item'):
        try:
            bgg_list.append([
                sydney_date,
                item.attrib['id'],
                item.attrib['type'],
                item.xpath('./name[@type="primary"]/@value')[0],
                f"https://boardgamegeek.com/boardgame/{item.attrib['id']}",
                item.xpath('./yearpublished/@value')[0],
                item.xpath('./minplayers/@value')[0],
                item.xpath('./maxplayers/@value')[0],
                item.xpath('./playingtime/@value')[0],
                item.xpath('./minplaytime/@value')[0],
                item.xpath('./maxplaytime/@value')[0],
                item.xpath('.//usersrated/@value')[0],
                item.xpath('.//average/@value')[0],
                item.xpath('.//stddev/@value')[0],
                item.xpath('.//bayesaverage/@value')[0],
                item.xpath('.//numcomments/@value')[0],
                item.xpath('.//numweights/@value')[0],
                item.xpath('.//averageweight/@value')[0],
                item.xpath('.//owned/@value')[0],
                item.xpath('.//wishing/@value')[0],
                item.xpath('.//trading/@value')[0],
                item.xpath('.//wanting/@value')[0],
                item.xpath('.//rank[@id="1"]/@value')[0],
                list_to_string(item.xpath('./link[@type="boardgamecategory"]/@id')),
                list_to_string(item.xpath('./link[@type="boardgamecategory"]/@value')),
                list_to_string(item.xpath('./link[@type="boardgamemechanic"]/@id')),
                list_to_string(item.xpath('./link[@type="boardgamemechanic"]/@value')),
                list_to_string(item.xpath('./link[@type="boardgamefamily"]/@id')),
                list_to_string(item.xpath('./link[@type="boardgamefamily"]/@value')),
                list_to_string(item.xpath('./link[@type="boardgamedesigner"]/@id')),
                list_to_string(item.xpath('./link[@type="boardgamedesigner"]/@value')),
                list_to_string(item.xpath('./link[@type="boardgamepublisher"]/@id')),
                list_to_string(item.xpath('./link[@type="boardgamepublisher"]/@value')),
                list_to_string(item.xpath('./link[@type="boardgameartist"]/@id')),
                list_to_string(item.xpath('./link[@type="boardgameartist"]/@value')),
            ])

            for result in item.xpath('./poll[@name="suggested_numplayers"]/results'):
                suggested_players_list.append([
                    sydney_date,
                    item.attrib['id'],
                    result.attrib['numplayers'],
                    list_to_string(result.xpath('./result/@value')),
                    list_to_string(result.xpath('./result/@numvotes')),
                ])
        except IndexError as error:
            logging.warning(f"issue with processing {item.attrib['id']} for {xml_path}. Skipping",exc_info=True)
        except Exception as error:
            logging.error(f"issue with processing {item.attrib['id']} for {xml_path}",exc_info=True)
            raise
    return bgg_list, suggested_players_list

def create_df(data_list: str, mode: str) -> pd.DataFrame:
    if mode == 'suggested_players':
        df_columns: list[str] = [
        'date',
        'bgg_id',
        'suggested_player_count',
        'player_count_rating',
        'player_count_votes',
        ]
        df_dtype = {
            'bgg_id':int,
            'suggested_player_count':str,
            'player_count_rating':str,
            'player_count_votes':str,
        }
    elif mode == 'bgg':
        df_columns: list[str] = [
            'date',
            'bgg_id',
            'type',
            'name',
            'url',
            'year_published',
            'min_players',
            'max_players',
            'play_time',
            'min_play_time',
            'max_play_time',
            'num_ratings',
            'avg_rating',
            'standard_deviation_rating',
            'bayesian_avg_rating',
            'num_comments',
            'num_complexity_ratings',
            'avg_complexity_rating',
            'num_own',
            'num_wishlist',
            'num_for_trade',
            'num_want_in_trade',
            'bgg_rank',
            'boardgame_category_id',
            'boardgame_category',
            'boardgame_mechanic_id',
            'boardgame_mechanic',
            'boardgame_family_id',
            'boardgame_family',
            'boardgame_designer_id',
            'boardgame_designer',
            'boardgame_publisher_id',
            'boardgame_publisher',
            'boardgame_artist_id',
            'boardgame_artist',
        ]
        df_dtype = {
            'bgg_id':int,
            'type':str,
            'name':str,
            'url':str,
            'year_published':int,
            'min_players':int,
            'max_players':int,
            'play_time':int,
            'min_play_time':int,
            'max_play_time':int,
            'num_ratings':int,
            'avg_rating':float,
            'standard_deviation_rating':float,
            'bayesian_avg_rating':float,
            'num_comments':int,
            'num_complexity_ratings':int,
            'avg_complexity_rating':float,
            'num_own':int,
            'num_wishlist':int,
            'num_for_trade':int,
            'num_want_in_trade':int,
            'bgg_rank':str,
            'boardgame_category_id':str,
            'boardgame_category':str,
            'boardgame_mechanic_id':str,
            'boardgame_mechanic':str,
            'boardgame_family_id':str,
            'boardgame_family':str,
            'boardgame_designer_id':str,
            'boardgame_designer':str,
            'boardgame_publisher_id':str,
            'boardgame_publisher':str,
            'boardgame_artist_id':str,
            'boardgame_artist':str,
        }

    df = pd.DataFrame(data_list, columns=df_columns)
    df['date'] = pd.to_datetime(df['date'])
    df = df.astype(df_dtype)
    return df

def process_xml(batch_number: int, xml_batch_paths:list[str], local_temp_path:str, stage_data_path:str, sydney_date) -> None:
    # Reads in a xml file on GCS, parses it and then saves it in GCS (parquet) and BQ
    combined_bgg_list = []
    combined_suggested_players_list = []
    i = 0
    for xml_path in xml_batch_paths:
        with open(xml_path,'r', encoding="utf-8") as f:
            xml = f.read()

        logging.debug(f'{xml_path} has been read')
        if (i+1) % 10 == 0:
            logging.info(f"{i+1} xml files read")        
        
        xml_data_bytes = xml.encode('utf-8')
        doc = etree.XML(xml_data_bytes)

        bgg_list, suggested_players_list = parse_xml(doc, sydney_date, xml_path)
        combined_bgg_list.extend(bgg_list)
        combined_suggested_players_list.extend(suggested_players_list)
        logging.debug(f'parsing completed for {xml_path}')
        if (i+1) % 10 == 0:
            logging.info(f"{i+1} xml files parsed")      
        i += 1
    
    df_bgg_chunk = create_df(combined_bgg_list,'bgg')
    df_suggested_players_chunk = create_df(combined_suggested_players_list,'suggested_players')

    local_destination_bgg = f"{local_temp_path}/{stage_data_path}/bgg_{batch_number}.parquet"
    local_destination_suggested_players = f"{local_temp_path}/{stage_data_path}/sp_{batch_number}.parquet"

    write_pq(df_bgg_chunk, local_destination_bgg)
    write_pq(df_suggested_players_chunk, local_destination_suggested_players)
    logging.info(f'created parquet files in {local_temp_path}/{stage_data_path}')

    return None

def write_pq(df:pd.DataFrame, local_destination: str) -> None:
    table = pa.Table.from_pandas(df)
    pq.write_table(table, local_destination)
    return None

def prepare_xml_batch_list(local_temp_path:str , raw_data_path:str ) -> list[int,list[str]]:
    xml_raw_path = f"{local_temp_path}/{raw_data_path}"
    xml_list = [f"{xml_raw_path}/{filename}" for filename in os.listdir(f"{xml_raw_path}")]
    
    xml_batch_size: int = 20
    xml_count: int = len(xml_list)
    xml_batch_count: int = math.ceil(xml_count/xml_batch_size)
    logging.info(f"{xml_batch_count} batches to be processed: {xml_count} total xml files with {xml_batch_size} xmls per batch")

    xml_batch_list: list[int,list[str]] = []
    for i in range(xml_batch_count):
        xml_sublist: list[str] = xml_list[i*xml_batch_size:(i+1)*xml_batch_size]
        xml_batch_list.append([i, xml_sublist])
    return xml_batch_list

def process_xmls(xml_batch_list:str, local_temp_path:str, stage_data_path:str, sydney_date) -> None:
    for batch_number, xml_batch_paths in xml_batch_list:
        logging.info(f"Processing batch {batch_number}")
        process_xml(batch_number, xml_batch_paths, local_temp_path, stage_data_path, sydney_date)
    return None

@custom
def main(*args, **kwargs):
    global logging
    logging = kwargs.get('logger')

    _, _, raw_data_path, stage_data_path, local_temp_path = folder_paths()
    sydney_date = get_date()
    xml_batch_list = prepare_xml_batch_list(local_temp_path, raw_data_path)
    process_xmls(xml_batch_list, local_temp_path, stage_data_path, sydney_date)
    return None