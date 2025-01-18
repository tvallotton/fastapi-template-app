from datetime import datetime
from typing import Annotated
from uuid import UUID, uuid4

from fastapi import Depends
from pydantic import BaseModel

from app.database import models
from app.database.repository import Repository
from app.utils import dependency


class Factory[T: models.BaseModel](BaseModel):
    repository: Repository[T]
    table_class: type

    def __class_getitem__(cls, model_type: type):  # type: ignore

        def factory(repository: Repository[model_type]):  # type: ignore
            return Factory(repository=repository, table_class=model_type)

        return Annotated[Factory, Depends(factory)]

    async def create(self, **data):
        from app.fake import fake

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
        await self.repository.save(record)
        return record
