from dataclasses import dataclass

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app import cron
from app.environment import DATABASE_URL, DEV_ENV
from app.utils import app_lifespan

from . import autoreload, database, home, user


@dataclass(frozen=True)
class AppConfig:
    DATABASE_URL: str = DATABASE_URL
    AUTORELOAD: bool = DEV_ENV


def create_app(config: AppConfig = AppConfig()) -> FastAPI:
    load_dotenv(".env")

    app = FastAPI(
        lifespan=app_lifespan(
            [
                database.lifespan.setup_database,
                cron.lifespan.setup_cron,
            ]
        )
    )

    app.state.config = config

    app.include_router(home.controller.router)
    app.include_router(user.controller.router)

    app.mount("/static", StaticFiles(directory="static"), name="static")

    if config.AUTORELOAD:
        app.include_router(autoreload.router)

    return app


app = create_app()
