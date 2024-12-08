import pandas as pd
import os
import logging

logger = logging.getLogger('app_logger')

ALLOWED_EXTENSIONS = {'csv'}

def get_file_statistics(df):
    """
    Calculate statistics for the given DataFrame.

    Returns:
        A dictionary with:
            - Number of columns
            - Number of observations
            - Number of missing values
            - Number and types of variables
    """
    try:
        num_columns = int(df.shape[1]) if df.shape[1] else 'N/A'
        num_observations = int(df.shape[0]) if df.shape[0] else 'N/A'
        missing_values = int(df.isnull().sum().sum()) if not df.empty else 'N/A'
        
        # Infer objects to refine data types
        df = df.infer_objects()

        # Detect datetimes explicitly
        variable_types = {}
        for column in df.columns:
            dtype = df[column].dtype
            if dtype == "object":
                # Check if the column can be parsed as datetime
                try:
                    pd.to_datetime(df[column], errors='raise')
                    variable_types[column] = "datetime"
                except (ValueError, TypeError):
                    variable_types[column] = "string"
            else:
                variable_types[column] = str(dtype)

        return {
            "num_columns": num_columns,
            "num_observations": num_observations,
            "missing_values": missing_values,
            "variable_types": variable_types
        }

    except Exception as e:
        logger.error(f"Error calculating file statistics: {str(e)}")
        return {
            "num_columns": "N/A",
            "num_observations": "N/A",
            "missing_values": "N/A",
            "variable_types": "N/A"
        }

def validate_csv_file(filename):
    """
    Validate if the uploaded file is a CSV file.
    """
    is_valid = '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    if is_valid:
        logger.debug(f"File {filename} passed validation.")
    else:
        logger.warning(f"File {filename} failed validation. Allowed extensions: {ALLOWED_EXTENSIONS}")
    return is_valid

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
