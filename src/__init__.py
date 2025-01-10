import os
from dataclasses import dataclass

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from . import autoreload, database, home, user


@dataclass(frozen=True)
class AppConfig:
    DATABASE_URL: str = os.environ["DATABASE_URL"]
    AUTORELOAD: bool = os.environ["ENV"] == "dev"


def create_app(config: AppConfig = AppConfig()) -> FastAPI:
    load_dotenv(".env")

    app = FastAPI(lifespan=database.lifespan.setup_database)

    app.state.config = config

    app.include_router(home.controller.router)
    app.include_router(user.controller.router)

    app.mount("/static", StaticFiles(directory="static"), name="static")

    if config.AUTORELOAD:
        app.include_router(autoreload.router)

    return app


app = create_app()
