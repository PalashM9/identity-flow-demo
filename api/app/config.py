from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://identity_user:identity_password_change_me@postgres:5432/identity_demo"
    api_username: str = "demo_user"
    api_password: str = "demo_password_change_me"

    webhook_url: str = "http://receiver:3001/webhooks/identity"
    webhook_secret: str = "local_webhook_secret_change_me"

    log_level: str = "INFO"


settings = Settings()