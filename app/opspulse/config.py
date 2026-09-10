from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "development"
    log_level: str = "INFO"

    database_url: str = "postgresql+asyncpg://opspulse:opspulse@localhost:5432/opspulse"

    # Demo-failure mechanism is a deliberate, reversible feature-flagged fault
    # injector for the demo scenario. It must never be reachable in "production".
    demo_mode_enabled: bool = True

    # AI Incident Assistant
    ai_backend: str = "fallback"  # "bedrock" | "mock" | "fallback"
    bedrock_model_id: str = "anthropic.claude-3-haiku-20240307-v1:0"
    aws_region: str = "us-east-1"
    ai_max_log_chars: int = 2000

    service_name: str = "opspulse"


settings = Settings()
