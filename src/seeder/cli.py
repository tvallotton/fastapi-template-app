import asyncio
import os

import asyncpg
import typer

from src.database.service import get_pg_connection
from src.seeder.service import SeederService
from src.utils import Injector

app = typer.Typer(no_args_is_help=True)


async def get_service(service_type):
    cnn = await asyncpg.connect(os.environ["DATABASE_URL"])
    return Injector(overrides={get_pg_connection: lambda: cnn}).get(service_type)


async def async_seed():
    seeder_service = await get_service(SeederService)
    await seeder_service.seed()
    typer.echo("seeding complete")


@app.command()
def seed():
    asyncio.run(async_seed())
