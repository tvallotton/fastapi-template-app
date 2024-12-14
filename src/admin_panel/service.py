from pydantic import BaseModel
from src.user.model import User
from src.admin_panel.forms import AdminQuery
from src.admin_panel.models import ColumnInfo
from src.database.service import Connection
from src.database.sqlformatter import SQLFormatter


class SchemaInfo(BaseModel):
    table_name: str
    rows: str


class AdminPanelService:

    models : list[type] = [User]

    model = {
        model.table_name(): model for model in models
    }

    def __init__(self, cnn: Connection):
        self.cnn = cnn
        self.formatter = SQLFormatter()

    async def has_history(self, table_name):
        record = await self.cnn.fetchrow(
            "admin_panel/has_history", table_name=table_name
        )
        return record["count"] != 0

    async def get_column_info(self, table_name):
        columns = await self.cnn.fetch(
            "admin_panel/get_column_info", table_name=table_name
        )
        return {column["column_name"]: ColumnInfo(**column) for column in columns}

    async def query_table(self, query: AdminQuery):
        records = await self.cnn.fetch("admin_panel/query_table")
        return records

    async def save_record(self, table_name: str, form: dict):
        model = self.model[table_name]
        record = model(**form)
        await record.save()

    async def delete_table(self, table_table: str, form: dict):
        self.model[table_table]
        raise NotImplementedError()
