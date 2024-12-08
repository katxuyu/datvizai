from .logging_config import logger

ALLOWED_EXTENSIONS = {'csv'}

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
