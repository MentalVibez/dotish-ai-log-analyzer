from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama2"

    # Optional: future providers
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None

    # Logging
    log_level: str = "INFO"

    # Limit log size sent to LLM
    max_log_lines: int = 5000

    # CORS: comma-separated origins or "*" (production: set to your front-end origin(s))
    cors_origins: str = "*"


settings = Settings()
