import re
import typing
from ast import TypeVar
from csv import Error
from datetime import datetime
from typing import Annotated, Any, NewType
from uuid import UUID, uuid4

from fastapi import Depends
from pydantic import BaseModel, ConfigDict

from src.database.service import Connection


class Repository[T](BaseModel):
    cnn: Connection
    table_class: Any

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __class_getitem__(self, model_type):

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

    async def save(self, model: T, path=None) -> T:
        dir = self.model_dir
        record = await self.cnn.fetchrow(path or f"{dir}/save", **model.model_dump())
        return self.table_class(**record)

    def transaction(self):
        return self.cnn.cnn.transaction()

    @property
    def model_dir(self):
        return self.table_name

    @property
    def table_name(self):
        name = self.table_class.__name__
        return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()

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
