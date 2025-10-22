from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "tecsys-backend"
    ROOT_PATH: str = '/'
    DATABASE_URL: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
