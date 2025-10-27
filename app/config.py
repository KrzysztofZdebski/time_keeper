import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key_here')
    
    # Google Cloud SQL Configuration (from environment variables)
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    PUBLIC_IP_ADDRESS = os.getenv('PUBLIC_IP_ADDRESS')
    DB_NAME = os.getenv('DB_NAME')
    PROJECT_ID = os.getenv('PROJECT_ID')
    INSTANCE_NAME = os.getenv('INSTANCE_NAME')

    # If Google Cloud SQL variables are set, use them. Otherwise, use SQLite for local development
    if all([DB_PASSWORD, PUBLIC_IP_ADDRESS, DB_NAME, PROJECT_ID, INSTANCE_NAME]):
        # Google Cloud SQL connection string
        SQLALCHEMY_DATABASE_URI = f"mysql+mysqldb://root:{DB_PASSWORD}@{PUBLIC_IP_ADDRESS}/{DB_NAME}?unix_socket=/cloudsql/{PROJECT_ID}:{INSTANCE_NAME}"
    else:
        # Local SQLite database for development
        SQLALCHEMY_DATABASE_URI = 'sqlite:///development.db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True