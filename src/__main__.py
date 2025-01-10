import asyncio
import os

import asyncpg
import typer
import uvicorn

from src.database.cli import app as database
from src.seeder.cli import app as seeder

app = typer.Typer(no_args_is_help=True)


@app.command()
def prod():
    """
    Runs the server in production mode.
    """
    os.environ["ENV"] == "prod"
    uvicorn.run("src:app", port=int(os.environ["PORT"]))


@app.command()
def dev():
    """
    Runs the server in development mode.
    """
    os.environ["ENV"] = "dev"
    uvicorn.run("src:app", port=int(os.environ["PORT"]), reload=True)


app.add_typer(
    database, name="database", help="Commands for migrating for dev and test databases"
)
app.add_typer(seeder, name="seed", help="Seeds the dev database")

if __name__ == "__main__":
    app()
