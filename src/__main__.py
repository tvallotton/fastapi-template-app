import os
from dataclasses import dataclass

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from . import autoreload, database, home, user


@dataclass(frozen=True)
class AppConfig:
    DATABASE_URL: str = os.environ["DATABASE_URL"]
    AUTORELOAD: bool = os.environ["ENV"] == "DEV"


def create_app(config: AppConfig = AppConfig()) -> FastAPI:

    app = FastAPI(lifespan=database.lifespan.setup_database)

    app.state.config = config

    app.include_router(home.controller.router)
    app.include_router(user.controller.router)

    app.mount("/static", StaticFiles(directory="static"), name="static")

    if config.AUTORELOAD:
        app.include_router(autoreload.router)

    return app


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        create_app(), port=int(os.environ["PORT"]), reload=os.environ["ENV"] == "DEV"
    )
