import asyncio
import os

import asyncpg
import typer

from app.database.service import get_pg_connection
from app.resolver import Resolver
from app.seeder.service import SeederService

app = typer.Typer(no_args_is_help=True)


async def get_service(service_type):
    cnn = await asyncpg.connect(os.environ["DATABASE_URL"])
    return Resolver(overrides={get_pg_connection: lambda: cnn}).get(service_type)


async def async_seed():
    seeder_service = await get_service(SeederService)
    await seeder_service.seed()
    typer.echo("seeding complete")


@app.command()
def seed():
    asyncio.run(async_seed())
