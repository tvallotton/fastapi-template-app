import os
import subprocess

import typer
import uvicorn

from app.database.cli import app as database
from app.environment import LOG_LEVEL
from app.seeder.cli import app as seeder

app = typer.Typer(no_args_is_help=True)


@app.command()
def prod():
    """
    Runs the server in production mode.
    """
    os.environ["ENV"] = "prod"
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=int(os.environ["PORT"]),
        log_level=LOG_LEVEL.lower(),
    )


@app.command()
def dev():
    """
    Runs the server in development mode.
    """
    os.environ["ENV"] = "dev"
    # fmt: off
    subprocess.Popen(
        ["npx", "tailwindcss", "-i", "./static/styles/input.css", "-o", "./static/styles/output.css", "--watch", "-y"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    # fmt: on
    uvicorn.run(
        "app:app",
        port=int(os.environ["PORT"]),
        reload=True,
        log_level=LOG_LEVEL.lower(),
    )


app.add_typer(
    database, name="database", help="Commands for migrating for dev and test databases"
)
app.add_typer(seeder, name="seeder", help="Seeds the dev database")

if __name__ == "__main__":
    app()
