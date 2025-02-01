from typing import Annotated
from uuid import UUID

from fastapi import Depends
from pydantic import BaseModel, ConfigDict

from app.database import models
from app.database.models import Savepoint
from app.database.service import Connection


class Repository[T: models.BaseModel](BaseModel):
    cnn: Connection
    table_class: type[T]

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __class_getitem__(cls, model_type):  # type: ignore

        def get_repository(cnn: Connection):
            return Repository(cnn=cnn, table_class=model_type)

        return Annotated[Repository, Depends(get_repository)]

    async def find_one(self, query="", **where) -> T | None:
        path = self.query_path("find_one", query)
        record = await self.cnn.fetchrow(path, **where)
        if record is not None:
            return self.table_class(**record)

    async def find(self, query="", **where):
        path = self.query_path("find", query)
        cursor = self.cnn.cursor(path, **where)
        async for record in cursor:
            yield self.table_class(**record)

    async def delete(self, id: str | UUID):
        path = self.query_path("delete", "")
        await self.cnn.execute(path, id=id)

    def query_path(self, prefix: str, query: str = ""):
        if query != "":
            return f"{self.model_dir}/{prefix}_{query}"
        else:
            return f"{self.model_dir}/{prefix}"

    async def count(self, query="", **kwargs) -> int:
        path = self.query_path("count", query)
        row = await self.cnn.fetchrow(path, **kwargs)
        assert row is not None
        return row["count"]

    async def savepoint(self) -> Savepoint:
        savepoint = Savepoint()
        await self.cnn.savepoint(savepoint.name)
        return savepoint

    def rollback(self, savepoint: Savepoint):
        return self.cnn.rollback(savepoint.name)

    async def save(self, model: T, path=None) -> T:
        dir = self.model_dir
        record = await self.cnn.fetchrow(path or f"{dir}/save", **model.model_dump())
        assert record is not None
        return self.table_class(**record)

    def transaction(self):
        return self.cnn.cnn.transaction()

    @property
    def model_dir(self):
        return self.table_class.model_dir()

    @property
    def table_name(self):
        return self.table_class.table_name()
