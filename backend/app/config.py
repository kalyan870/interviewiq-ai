from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    openai_api_key: str | None = None
    openai_model: str = "gpt-4.1-mini"
    allowed_origins: str = "http://localhost:3000"


settings = Settings()
