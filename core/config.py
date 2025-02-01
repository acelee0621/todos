from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl
from dotenv import load_dotenv
from functools import lru_cache
from typing import Any

load_dotenv(".env")


class Settings(BaseSettings):
    app_name: str = "Todos API"
    JWT_SECRET: str
    JWT_ALGORITHM: str
    JWT_LIFETIME_SECONDS: int = 60 * 60 * 12

    CORS_ORIGINS: list[AnyHttpUrl] = ["http://localhost:3000", "http://127.0.0.1:8000"]

    class Config:
        env_file = ".env"
        case_sensitive = True

        @classmethod
        def parse_env_var(cls, field_name: str, raw_val: str) -> Any:
            if field_name == "CORS_ORIGINS":
                return [origin for origin in raw_val.split(";")]
            # The following line is ignored by mypy because:
            # error: Type'[Config]' has no attribute 'json_loads',
            # even though it is like the documentation: https://docs.pydantic.dev/latest/usage/settings/
            return cls.json_loads(raw_val)  # type: ignore[attr-defined]


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()
