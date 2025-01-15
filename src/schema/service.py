"""
Service related to querying the database schema.
"""


from fastapi import Depends
from pydantic import BaseModel, ConfigDict

from src.database.service import Connection
from src.schema.models import ColumnInfo
from src.utils import dependency


@dependency()
class SchemaService(BaseModel):
    cnn: Connection

    model_config = ConfigDict(arbitrary_types_allowed=True)

    async def has_history(self, table_name: str):
        record = await self.cnn.fetchrow("schema/has_history", table_name=table_name)
        assert record is not None
        return record["count"] != 0

    async def get_column_info(self, table_name) -> dict[str, ColumnInfo]:
        assert await self.table_exists(table_name=table_name)
        columns = await self.cnn.fetch("schema/get_column_info", table_name=table_name)
        return {column["column_name"]: ColumnInfo(**column) for column in columns}

    async def table_exists(self, table_name: str):
        record = await self.cnn.fetchrow("schema/table_exists", table_name=table_name)
        assert record is not None
        return record["exists"]
