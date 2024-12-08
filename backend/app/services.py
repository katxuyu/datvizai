import pandas as pd
from .logging_config import logger

def parse_csv(filepath):
    """
    Parse the CSV file into a tabular format and return the data as a dictionary.
    """
    try:
        logger.info(f"Parsing CSV file: {filepath}")
        df = pd.read_csv(filepath)
        logger.debug(f"Parsed DataFrame: {df.head()}")
        return df.to_dict(orient='records')  # Convert to a list of dictionaries (tabular format)
    except Exception as e:
        logger.error(f"Error parsing CSV file {filepath}: {str(e)}")
        raise ValueError(f"Error parsing CSV file: {str(e)}")
