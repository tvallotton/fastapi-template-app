from typing import Annotated

from fastapi import Form
from pydantic import BaseModel, Field


class Pagination(BaseModel):
    limit: int = Field(le=30, default=15)
    offset: int = 0
    order_by: str = "id"


Pagination = Annotated[Pagination, Form()]
