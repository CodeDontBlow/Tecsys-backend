from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "tecsys-backend"
    ROOT_PATH: str = '/'


settings = Settings()
