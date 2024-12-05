import os
from contextlib import asynccontextmanager
from dataclasses import dataclass

import asyncpg
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from . import autoreload, home, user


@dataclass(frozen=True)
class AppConfig:
    DATABASE_URL: str = os.environ["DATABASE_URL"]
    AUTORELOAD: bool = os.environ["ENV"] == "DEV"


@asynccontextmanager
async def setup_db(app: FastAPI):
    app.state.db_pool = await asyncpg.create_pool(app.state.config.DATABASE_URL)
    yield
    await app.state.db_pool.close()


def create_app(config: AppConfig = AppConfig()) -> FastAPI:

    app = FastAPI(lifespan=setup_db)
    app.state.config = config

    app.include_router(home.routes.router)
    app.include_router(user.routes.router)

    app.mount("/static", StaticFiles(directory="static"), name="static")

    if config.AUTORELOAD:
        app.include_router(autoreload.router)

    return app


app = create_app()
