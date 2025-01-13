import asyncio
import os
import subprocess
from datetime import timedelta

import asyncpg
import pgqueuer
import pgqueuer.supervisor
import rich
import typer
import uvicorn
import uvloop
import watchfiles

from src.database.cli import app as database
from src.queue.cli import create_pgq
from src.seeder.cli import app as seeder

app = typer.Typer(no_args_is_help=True)


@app.command()
def prod():
    """
    Runs the server in production mode.
    """
    os.environ["ENV"] = "prod"
    uvicorn.run("src:app", host="0.0.0.0", port=int(os.environ["PORT"]))


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
    subprocess.Popen(
        ["watchfiles", "pgq run src.queue.cli:create_pgq", "src"]
    )
    # fmt: on
    uvicorn.run("src:app", port=int(os.environ["PORT"]), reload=True)


@app.command()
def queue(
    dequeue_timeout: float = typer.Option(30.0, "--dequeue-timeout"),
    batch_size: int = typer.Option(10, "--batch-size"),
    restart_delay: float = typer.Option(5.0, "--restart-delay"),
    restart_on_failure: bool = typer.Option(False, "--restart-on-failure"),
):
    """
    Runs the consumer queue
    """
    rich.print("[blue]Starting worker queue.[/blue]")

    uvloop.run(
        pgqueuer.supervisor.runit(
            create_pgq,
            dequeue_timeout=timedelta(seconds=dequeue_timeout),
            batch_size=batch_size,
            restart_delay=timedelta(seconds=restart_delay if restart_on_failure else 0),
            restart_on_failure=restart_on_failure,
            shutdown=asyncio.Event(),
        )
    )


app.add_typer(
    database, name="database", help="Commands for migrating for dev and test databases"
)
app.add_typer(seeder, name="seed", help="Seeds the dev database")

if __name__ == "__main__":
    app()
