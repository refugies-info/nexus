from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration using Pydantic BaseSettings."""

    # Application
    app_name: str = "Nexus Orchestration Service"
    app_version: str = "0.1.0"
    debug: bool = False
    environment: str = "development"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False

    # Supabase
    supabase_url: str
    supabase_key: str
    supabase_pool_size: int = 10
    supabase_pool_timeout: int = 30

    # Database
    database_url: str | None = None

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"

    # API
    api_prefix: str = "/api/v1"
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    openapi_url: str = "/openapi.json"

    # Data Inclusion API
    data_inclusion_api_url: str = "https://api.data-inclusion.beta.gouv.fr"
    data_inclusion_api_timeout: int = 30

    # Carif-Oref
    carif_oref_csv_url: str = "https://www.intercariforef.org/dian/?excsv=1"
    carif_oref_csv_refresh_interval: int = 3600  # 1 hour in seconds

    # Pipeline
    max_retries: int = 3
    retry_delay: int = 5  # seconds
    stage_timeout: int = 300  # 5 minutes in seconds

    # Update handling
    update_check_interval: int = 300  # 5 minutes in seconds
    smart_catchup_enabled: bool = True
    risk_sampling_threshold_high: float = 0.8
    risk_sampling_threshold_medium: float = 0.5
    risk_sampling_medium_percentage: int = 20  # 20% of medium-risk diffs

    # Observability
    sentry_dsn: str | None = None
    enable_metrics: bool = True
    metrics_port: int = 9090

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


def get_settings() -> Settings:
    """Get application settings (singleton pattern)."""
    return Settings()
