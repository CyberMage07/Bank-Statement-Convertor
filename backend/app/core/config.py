from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "FinDoc AI"
    environment: str = "development"
    database_url: str = "postgresql+psycopg://findoc:findoc@db:5432/findoc"
    redis_url: str = "redis://redis:6379/0"
    s3_bucket: str = "findoc-documents"
    s3_endpoint_url: str = "http://minio:9000"
    stripe_webhook_secret: str = "whsec_placeholder"
    jwt_secret: str = "change-me"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
