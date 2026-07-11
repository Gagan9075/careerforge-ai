from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str
    app_version: str
    environment: str

    database_url: str

    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    ai_provider: str
    gemini_api_key: str = ""
    ollama_url: str

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
    )


settings = Settings()