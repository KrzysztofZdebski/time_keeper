import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key_here')
    
    # Google Cloud SQL Configuration (from environment variables)
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_NAME = os.getenv('DB_NAME')
    # Cloud SQL connection name format: project_id:region:instance_name
    CLOUD_SQL_CONNECTION_NAME = os.getenv('CLOUD_SQL_CONNECTION_NAME')
    
    # For local development with public IP
    PUBLIC_IP_ADDRESS = os.getenv('PUBLIC_IP_ADDRESS')
    
    # Detect if running on Cloud Run
    IS_CLOUD_RUN = os.getenv('K_SERVICE') is not None

    # If Google Cloud SQL variables are set, use them. Otherwise, use SQLite for local development
    if all([DB_PASSWORD, DB_NAME, CLOUD_SQL_CONNECTION_NAME]):
        if IS_CLOUD_RUN:
            # Cloud Run: use Unix socket (like the example snippet)
            SQLALCHEMY_DATABASE_URI = (
                f"mysql+mysqldb://{DB_USER}:{DB_PASSWORD}@/{DB_NAME}"
                f"?unix_socket=/cloudsql/{CLOUD_SQL_CONNECTION_NAME}"
            )
        elif PUBLIC_IP_ADDRESS:
            # Local/Docker: use TCP connection
            SQLALCHEMY_DATABASE_URI = (
                f"mysql+mysqldb://{DB_USER}:{DB_PASSWORD}@{PUBLIC_IP_ADDRESS}:3306/{DB_NAME}"
            )
        else:
            # Fallback to SQLite
            SQLALCHEMY_DATABASE_URI = 'sqlite:///development.db'
    else:
        # Local SQLite database for development
        SQLALCHEMY_DATABASE_URI = 'sqlite:///development.db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True