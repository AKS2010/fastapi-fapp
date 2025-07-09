from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from WrapperFunction.core.config import settings
import time
from urllib.parse import quote_plus
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import text

def get_engine():
    max_retries = 3
    retry_delay = 5  # seconds

    # Get database connection details from environment variables
    DB_SERVER = settings.DB_SERVER
    DB_NAME = settings.DB_NAME
    DB_USER = settings.DB_USER
    DB_PASSWORD = settings.DB_PASSWORD
    DB_DRIVER = settings.DB_DRIVER

    # Construct the connection string for Azure SQL Database
    conn_str = (
        f"Driver={{{DB_DRIVER}}};"
        f"Server=tcp:{DB_SERVER},1433;"
        f"Database={DB_NAME};"
        f"Uid={DB_USER};"
        f"Pwd={DB_PASSWORD};"
        "Encrypt=yes;"
        "TrustServerCertificate=no;"
        "Connection Timeout=30;"
    )

    # Create SQLAlchemy URL
    SQLALCHEMY_DATABASE_URL = f"mssql+pyodbc:///?odbc_connect={quote_plus(conn_str)}"    
    for attempt in range(max_retries):
        try:
            # Create SQLAlchemy engine
            engine = create_engine(
                SQLALCHEMY_DATABASE_URL,
                pool_size=5,
                max_overflow=10,
                pool_timeout=30,
                pool_recycle=1800,  # Recycle connections after 30 minutes
                echo=False  # Set to True for debugging
            )
            
            # Test the connection
            with engine.connect() as connection:
                print("Database connection successful!")
                return engine
                
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Connection attempt {attempt + 1} failed: {str(e)}")
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print(f"Failed to connect after {max_retries} attempts")
                raise

# Initialize the engine
engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_direct_connection():
    """Test database connection during startup"""
    try:
        from WrapperFunction.db.session import engine
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(str(e))
        return False