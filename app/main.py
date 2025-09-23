from fastapi import FastAPI

from app.core.config import settings
from app.api.routers import api_router


class App(FastAPI):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(
            *args,
            **kwargs,
            version="0.1.0",
            title=settings.PROJECT_NAME,
            root_path=settings.ROOT_PATH
        )


app = App()
app.include_router(api_router, prefix="/api")
