from contextlib import asynccontextmanager

import asyncpg
from fastapi import FastAPI


@asynccontextmanager
async def setup_database(app: FastAPI):
    app.state.db_pool = await asyncpg.create_pool(app.state.config.DATABASE_URL)
    yield
    await app.state.db_pool.close()
