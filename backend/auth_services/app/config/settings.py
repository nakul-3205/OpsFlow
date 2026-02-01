from pydantic_settings import BaseSettings , SettingsConfigDict
import os
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
ENV_PATH = ROOT_DIR / ".env"
class Settings(BaseSettings):
    database_url:str

    model_config = SettingsConfigDict(env_file=ENV_PATH,case_sensitive=False,extra='allow')


settings=Settings()