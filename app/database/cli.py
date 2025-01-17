import os

import rich
from typer import Typer

app = Typer(no_args_is_help=True)

TEST_DATABASE_URL = os.environ["TEST_DATABASE_URL"]
DATABASE_URL = os.environ["DATABASE_URL"]


@app.command()
def reset(database_url: str = DATABASE_URL, test_database_url: str = TEST_DATABASE_URL):
    rich.print("[bold blue]Setup development database[/bold blue]")
    os.system(f"sqlx database reset --database-url {database_url} -y -f")
    rich.print("[bold blue]Setup testing database[/bold blue]")
    os.system(f"sqlx database reset --database-url {test_database_url} -y -f")


@app.command()
def migrate(
    database_url: str = DATABASE_URL, test_database_url: str = TEST_DATABASE_URL
):
    rich.print("[bold blue]Migrate development database[/bold blue]")
    os.system(f"sqlx migrate run --database-url {database_url} -y -f")
    rich.print("[bold blue]Migrate testing database[/bold blue]")
    os.system(f"sqlx migrate run --database-url {test_database_url} -y -f")
