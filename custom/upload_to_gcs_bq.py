if 'custom' not in globals():
    from mage_ai.data_preparation.decorators import custom
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@custom
def main(df_bgg_chunk, df_suggested_players_chunk, *args, **kwargs):
    """
    args: The output from any upstream parent blocks (if applicable)

    Returns:
        Anything (e.g. data frame, dictionary, array, int, str, etc.)
    """
    # Specify your custom logic here

    # Creates df and writes to GCS (parquet) and BQ
    # gcs_destination: str = f"gs://{os.getenv('GCS_BUCKET_NAME')}/{stage_data_path}"
    # for data_list, mode in zip([combined_bgg_list, combined_suggested_players_list],['bgg', 'suggested_players']):
    #     df = create_df(data_list, mode)
    #     logging.info(f'{mode} dataframe created for {len(xml_sublist)} xml files')
        
        # final_destination: str = f"{gcs_destination}/{mode}/{batch_number}.parquet"
        # write_pq(df, final_destination)
        # logging.info(f'{mode} parquet written at {final_destination}')

        # sydney_date = get_date()
        # bq_final_destination = "{os.getenv('GCP_PROJECT_ID')}.boardgamegeek_stage.{sydney_date}_{mode}"
        # write_bq(df,bq_final_destination)
        # logging.info(f'{mode} replaced {bq_final_destination}')


# def write_bq(df:pd.DataFrame, bq_destination: str) -> None:
#     pandas_gbq.to_gbq(
#         df,
#         bq_destination,
#         project_id=os.getenv('GCP_PROJECT_ID'),
#         if_exists='append',
#         credentials=bq_credentials,
#     )
#     return None

    return None


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
