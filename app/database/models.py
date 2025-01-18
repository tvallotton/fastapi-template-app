import re
from datetime import datetime
from uuid import UUID, uuid4

import pydantic
from pydantic import Field



class BaseModel(pydantic.BaseModel):
    id: UUID = Field(default_factory=uuid4)
    valid_since: datetime | None = None
    valid_until: datetime | None = None

    @classmethod
    def model_dir(cls):
        return cls.table_name()

    @classmethod
    def table_name(cls):
        name = cls.__name__
        return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


class Savepoint(BaseModel):
    name: str = Field(default_factory=lambda: str(uuid4()))
