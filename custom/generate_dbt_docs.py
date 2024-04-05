import subprocess

if 'custom' not in globals():
    from mage_ai.data_preparation.decorators import custom
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

@custom
def main(*args, **kwargs) -> None:
    global logging
    logging = kwargs.get('logger')

    result = subprocess.run(['dbt', 'deps'], capture_output=True, text=True)
    logging.info(result.stdout)

    result = subprocess.run(['dbt', 'docs', 'generate'], capture_output=True, text=True)
    logging.info(result.stdout)
    return None