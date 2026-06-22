from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    service_name: str = "fasa-social-dashboard"
    frontend_origin: str = "http://localhost:5173"

    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_database: str = "fasa_social"
    mysql_user: str = "fasa_social"
    mysql_password: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
