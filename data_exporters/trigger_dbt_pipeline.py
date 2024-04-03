from mage_ai.orchestration.triggers.api import trigger_pipeline
if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter

@data_exporter
def trigger(*args, **kwargs):
    trigger_pipeline(
    'boardgamegeek_dbt',
    check_status=False,
    error_on_failure=False,
    verbose=False,
    )
