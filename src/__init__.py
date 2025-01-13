import os
from dataclasses import dataclass

import asyncpg
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pgqueuer import AsyncpgPoolDriver

from src.environment import DATABASE_URL, DEV_ENV
from src.queue.cli import create_pgq

from . import autoreload, database, home, user


@dataclass(frozen=True)
class AppConfig:
    DATABASE_URL: str = DATABASE_URL
    AUTORELOAD: bool = DEV_ENV


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
