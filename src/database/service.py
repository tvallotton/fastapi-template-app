from copyreg import constructor
from pathlib import Path
from typing import Annotated

import asyncpg
from asyncpg.protocol import Record
from fastapi import Depends, Request

from src.database.sqlformatter import SQLFormatter
from src.utils import dependency

pg: asyncpg.Pool | None = None  # type: ignore

queries = {}

for file in Path(".").glob("sql/**/*.sql"):
    with open(file) as f:
        queries[str(file)[4:-4]] = f.read()


async def get_pg_connection(request: Request):
    pool = request.app.state.db_pool
    async with pool.acquire() as cnn:
        yield cnn


@dependency()
class Connection:
    def __init__(self, cnn: Annotated[asyncpg.Connection, Depends(get_pg_connection)]):
        self.cnn = cnn
        self.formatter = SQLFormatter()

    def fetch(self, path: str, *args, **kwargs):
        query = self.formatter.format(queries[path], *args, **kwargs)
        return self.cnn.fetch(query)

    def fetchrow(self, path: str, *args, **kwargs) -> Record:
        query = self.formatter.format(queries[path], *args, **kwargs)
        return self.cnn.fetchrow(query)

    def execute(self, path: str, *args, **kwargs):
        query = self.formatter.format(queries[path], *args, **kwargs)
        return self.cnn.execute(query)

    def cursor(self, path: str, *args, **kwargs):
        query = self.formatter.format(queries[path], *args, **kwargs)
        return self.cnn.cursor(query)

    def rollback(self):
        return self.cnn.execute("rollback")

    async def column_names(self, data: list, query: str):
        if len(data) != 0:
            return list(data[0].keys())

        stmt = await self.cnn.prepare(query)
        return [attr.name for attr in stmt.get_attributes()]
