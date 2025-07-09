from dotenv import load_dotenv
load_dotenv()
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_SERVER: str
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_DRIVER: str
    ADLS_STORAGE_ACCOUNT: str
    ADLS_STORAGE_KEY: str
    ADLS_CONTAINER: str
    HOST: str

    class Config:
        env_file = ".env"

settings = Settings()
