from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "dev"
    jwt_secret_key: str = "change-this-in-prod"
    jwt_algorithm: str = "HS256"
    jwt_access_ttl_min: int = 15
    google_vision_timeout_ms: int = 2200
    scan_max_retry: int = 5
    scan_ocr_engine: str = "google_vision"
    admin_emails: str = "admin@halalseoul.kr"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
