import os
from contextlib import asynccontextmanager
from pathlib import Path
from string import Formatter
from typing import Annotated

import asyncpg
from asyncpg.protocol import Record
from fastapi import Depends, Request
from pydantic import BaseModel
from pydantic.config import ConfigDict

from src.database.sqlformatter import SQLFormatter

pg: asyncpg.Pool | None = None  # type: ignore


queries = {}

for file in Path(".").glob("sql/**/*.sql"):
    with open(file) as f:
        queries[str(file)[4:-4]] = f.read()


async def get_pg_connection(request: Request):
    pool = request.app.state.db_pool
    async with pool.acquire() as cnn:
        yield cnn


class Connection:
    def __init__(self, cnn: Annotated[asyncpg.Connection, Depends(get_pg_connection)]):
        self.inline = cnn
        self.formatter = SQLFormatter()

    def fetch(self, path: str, *args, **kwargs):
        query = self.formatter.format(queries[path], *args, **kwargs)
        return self.inline.fetch(query)

    def fetchrow(self, path: str, *args, **kwargs) -> Record:
        query = self.formatter.format(queries[path], *args, **kwargs)
        return self.inline.fetchrow(query)

    def execute(self, path: str, *args, **kwargs):
        query = self.formatter.format(queries[path], *args, **kwargs)
        return self.inline.execute(query)

    def cursor(self, path: str, *args, **kwargs):
        query = self.formatter.format(queries[path], *args, **kwargs)
        return self.inline.cursor(query)

    def rollback(self):
        return self.inline.execute("rollback")

    async def fetch_with_colnames(self, path: str, *args, **kwargs):
        query = self.formatter.format(queries[path], *args, **kwargs)
        data = await self.inline.fetch(query)
        columns = await self.column_names(data, query)
        return FetchWithColNames(rows=data, columns=columns)

    async def column_names(self, data: list, query: str):
        if len(data) != 0:
            return list(data[0].keys())

        stmt = await self.inline.prepare(query)
        return [attr.name for attr in stmt.get_attributes()]


Connection = Annotated[Connection, Depends(Connection)]


class FetchWithColNames(BaseModel):
    rows: list[Record]
    columns: list[str]

    model_config = ConfigDict(arbitrary_types_allowed=True)
