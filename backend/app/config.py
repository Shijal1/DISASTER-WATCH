from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    APP_NAME: str = "DISASTERWATCH"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    DATABASE_URL: str = "sqlite:///./data/disasterwatch.db"
    USGS_POLL_INTERVAL: int = 300
    EONET_POLL_INTERVAL: int = 600
    GDACS_POLL_INTERVAL: int = 900
    COPERNICUS_CLIENT_ID: str = ""
    COPERNICUS_CLIENT_SECRET: str = ""
    FRONTEND_ORIGIN: str = "http://localhost:5173"
settings = Settings()