from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache





class Settings(BaseSettings):
    app_name: str = "Todos API"
    JWT_SECRET: str
    JWT_ALGORITHM: str
    JWT_LIFETIME_SECONDS: int = 60 * 60 * 12
    DEBUG: bool = False

    model_config = SettingsConfigDict(env_file=("./.env", ".env.local"))
        


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()
