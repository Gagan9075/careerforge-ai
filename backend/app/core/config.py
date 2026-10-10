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

    adzuna_app_id: str
    adzuna_app_key: str

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
    )

    resend_api_key: str | None = None
    email_from: str = "onboarding@resend.dev"
    resend_test_email: str | None = None


settings = Settings()