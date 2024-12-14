from pydantic import BaseModel


class ColumnInfo(BaseModel):
    column_name: str
    data_type: str
    is_required: bool
    is_nullable: bool
    foreign_table: str | None
    foreign_column: str | None
