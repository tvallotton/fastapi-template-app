from datetime import datetime
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


class TableReference(BaseModel):
    column_name: str
    reference_table_name: str
    reference_column_name: str
