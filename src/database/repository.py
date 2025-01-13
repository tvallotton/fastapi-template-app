import re
from datetime import datetime
from typing import Annotated, Any
from uuid import UUID, uuid4

from fastapi import Depends
from pydantic import BaseModel, ConfigDict

from src.database import models
from src.database.models import Savepoint
from src.database.service import Connection


class Repository[T: models.BaseModel](BaseModel):
    cnn: Connection
    table_class: type[T]

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __class_getitem__(cls, model_type):  # type: ignore

        def get_repository(cnn: Connection):
            return Repository(cnn=cnn, table_class=model_type)

        return Annotated[Repository, Depends(get_repository)]

    async def find_one(self, path=None, **where) -> T | None:
        record = await self.cnn.fetchrow(path or f"{self.model_dir}/find_one", **where)
        if record is not None:
            return self.table_class(**record)

    async def find(self, path=None, **where) -> list[T]:
        records = await self.cnn.fetch(path or f"{self.model_dir}/find", **where)
        return [self.table_class(**record) for record in records]

    async def delete(self, id: str | UUID):
        dir = self.model_dir
        await self.cnn.execute(f"{dir}/delete", id=id)

    async def count(self) -> int:
        dir = self.model_dir
        row = await self.cnn.fetchrow(f"{dir}/count")
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

    async def fake(self, **data):
        from src.faker import fake

        for field, info in self.table_class.model_fields.items():
            type = info.annotation
            if field in data:
                continue
            if type == str:
                data[field] = fake.text(max_nb_chars=100)
            elif type == int:
                data[field] = fake.random_int()
            elif type == float:
                data[field] = fake.pyfloat()
            elif type == datetime:
                data[field] = fake.date_time_this_year()
            elif type == UUID:
                data[field] = uuid4()

        record = self.table_class(**data)
        await self.save(record)
        return record
