from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Media QA"
    env: str = "dev"
    database_url: str = "mysql+pymysql://mediaqa:mediaqa@db:3306/mediaqa"
    openai_api_key: str = ""
    model_name: str = "gpt-4o-mini"
    upload_dir: str = "./uploads"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
