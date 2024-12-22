import re
from datetime import datetime
from uuid import UUID, uuid4

import pydantic
from pydantic import Field

from src.database.service import Connection


class BaseModel(pydantic.BaseModel):
    id: UUID = Field(default_factory=uuid4)
    valid_since: datetime | None = None
    valid_until: datetime | None = None

    @classmethod
    async def find_one(cls, cnn: Connection, path=None, **where):
        record = await cnn.fetchrow(path or f"{cls.model_dir()}/find_one", **where)
        if record is not None:
            return cls(**record)

    @classmethod
    async def find(cls, cnn: Connection, path=None, **where):
        records = await cnn.fetchrow(path or f"{cls.model_dir()}/find", **where)
        return [cls(**record) for record in records]

    async def delete(self, cnn: Connection):
        dir = self.model_dir()
        await cnn.execute(f"{dir}/delete", id=self.id)

    async def save(self, cnn):
        dir = self.model_dir()
        record = await cnn.fetchrow(f"{dir}/save", **self.model_dump())
        if record:
            return type(self)(**record)

    @classmethod
    def model_dir(cls):
        return cls.table_name()

    @classmethod
    def table_name(cls):
        name = cls.__name__
        return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()

    @classmethod
    async def fake(cls, cnn: Connection, **data):
        from src.faker import fake

        for field, info in cls.model_fields.items():
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
        record = cls(**data)
        await record.save(cnn)
        return record
