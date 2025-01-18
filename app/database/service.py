import logging
from pathlib import Path
from typing import Annotated

import asyncpg
from fastapi import Depends, Request

from app.database.logger import log_sql
from app.database.sqlformatter import SQLFormatter
from app.utils import dependency

queries = {}

for file in Path(".").glob("sql/**/*.sql"):
    with open(file) as f:
        queries[str(file)[4:-4]] = f.read()


async def get_pg_pool(request: Request):
    return request.app.state.db_pool


async def get_pg_connection(pool: Annotated[asyncpg.Pool, Depends(get_pg_pool)]):
    async with pool.acquire() as cnn:
        yield cnn


@dependency()
class Connection:
    def __init__(self, cnn: Annotated[asyncpg.Connection, Depends(get_pg_connection)]):
        self.cnn = cnn
        self.formatter = SQLFormatter()

    def fetch(self, path: str, *args, **kwargs):
        query = self.formatter.format(queries[path], *args, **kwargs)
        log_sql(query)
        return self.cnn.fetch(query)

    def fetchrow(self, path: str, *args, **kwargs):
        query = self.formatter.format(queries[path], *args, **kwargs)
        log_sql(query)
        return self.cnn.fetchrow(query)

    def execute(self, path: str, *args, **kwargs):
        query = self.formatter.format(queries[path], *args, **kwargs)
        log_sql(query)
        return self.cnn.execute(query)

    def cursor(self, path: str, *args, **kwargs):
        query = self.formatter.format(queries[path], *args, **kwargs)
        log_sql(query)
        return self.cnn.cursor(query)

    def rollback(self, savepoint: str):
        query = self.formatter.format(queries["database/rollback"], savepoint=savepoint)
        log_sql(query)
        return self.cnn.execute(query)

    def savepoint(self, name: str):
        query = self.formatter.format(queries["database/savepoint"], savepoint=name)
        log_sql(query)
        return self.cnn.execute(query)

    async def column_names(self, data: list, query: str):
        if len(data) != 0:
            return list(data[0].keys())

        stmt = await self.cnn.prepare(query)
        return [attr.name for attr in stmt.get_attributes()]
