from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "dev"
    jwt_secret_key: str = "change-this-in-prod"
    jwt_algorithm: str = "HS256"
    jwt_access_ttl_min: int = 15

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
