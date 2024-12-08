import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev')
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
