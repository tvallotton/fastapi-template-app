from datetime import datetime
from types import NotImplementedType
from typing import Type
from uuid import UUID

from pydantic import BaseModel


class ColumnInfo(BaseModel):
    column_name: str
    data_type: str
    is_required: bool
    is_nullable: bool
    foreign_table: str | None
    foreign_column: str | None

    @property
    def python_type(self) -> type:
        match self.data_type:
            case "text" | "character varying":
                return str
            case "uuid":
                return UUID
            case "timeztamp" | "timestamp with timezone":
                return datetime
            case "float" | "double precision":
                return float
            case "integer" | "bigint" | "smallint":
                return int
            case "bool":
                return bool
            case "json":
                return str
        raise NotImplementedError()
