import os
import psycopg2
from psycopg2.extras import RealDictCursor
from cryptography.fernet import Fernet
from .logging_config import logger
import hashlib

# Retrieve encryption key from environment variables
ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')

if not ENCRYPTION_KEY:
    logger.critical("ENCRYPTION_KEY is missing in environment variables.")
    raise ValueError("Missing ENCRYPTION_KEY environment variable.")

cipher = Fernet(ENCRYPTION_KEY.encode())  # Ensure it's bytes


class Database:
    def __init__(self):
        self.connection = None
        logger.info("Database instance created.")
        

    def connect(self):
        if not self.connection:
            try:
                logger.debug("Initializing database connection...")
                self.connection = psycopg2.connect(
                    host=os.getenv('DB_HOST', 'localhost'),
                    database=os.getenv('DB_NAME', 'default_db'),
                    user=os.getenv('DB_USER', 'default_user'),
                    password=os.getenv('DB_PASSWORD', 'default_password'),
                    port=os.getenv('DB_PORT', '5432'),  # Default PostgreSQL port
                    cursor_factory=RealDictCursor,
                    sslmode="require"
                )
                logger.info("Database connection established.")
            except Exception as e:
                logger.error(f"Failed to connect to the database: {str(e)}")
                raise


    def query(self, sql, params=None):
        self.connect()
        try:
            with self.connection.cursor() as cursor:
                logger.debug(f"Executing query: {sql} | Params: {params}")
                cursor.execute(sql, params)
                if cursor.description:
                    result = cursor.fetchall()
                    logger.debug(f"Query result: {result}")
                    return result
                self.connection.commit()
                logger.info("Query executed successfully.")
        except Exception as e:
            # Rollback the transaction on failure
            self.connection.rollback()
            logger.error(f"Database query failed: {str(e)}")
            raise


    def close(self):
        if self.connection:
            logger.info("Closing database connection.")
            self.connection.close()
            self.connection = None



# Encryption and decryption helpers
def encrypt(data):
    """
    Encrypts a string using the Fernet cipher.
    """
    return cipher.encrypt(data.encode()).decode()


def decrypt(data):
    """
    Decrypts a string using the Fernet cipher.
    """
    return cipher.decrypt(data.encode()).decode()

def hash_ip(ip):
    """
    Hashes the IP address using SHA-256 for consistency.
    """
    return hashlib.sha256(ip.encode()).hexdigest()