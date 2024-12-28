#!python
import asyncio
import os
import sys
from os import environ, mkdir

import asyncpg
from pydantic import BaseModel

from src.database.service import Connection
from src.schema.models import ColumnInfo
from src.schema.service import SchemaService

DATABASE_URL = environ["DATABASE_URL"]


async def get_columns(table_name):
    cnn = Connection(await asyncpg.connect(DATABASE_URL))

    cnn._column_names()
    "database/columns"


def mkfile(filename, output):
    with open(filename, "w") as f:
        f.write(output)


class ScaffoldOptions(BaseModel):
    snake_case: str
    models: bool
    controller: bool
    forms: bool
    service: bool
    templates: bool

    @property
    def pascal_case(self):
        return "".join(x.capitalize() for x in self.snake_case.lower().split("_"))

    @staticmethod
    def from_args():
        assert len(sys.argv) >= 2, "Excepted at least 1 argument"
        crud = "crud" in sys.argv[1:]
        return ScaffoldOptions(
            snake_case=sys.argv[1],
            models=crud or "models" in sys.argv[1:],
            controller=crud or "controller" in sys.argv[1:],
            service=crud or "service" in sys.argv[1:],
            templates=crud or "templates" in sys.argv[1:],
            forms=crud or "forms" in sys.argv[1:],
        )


class ScaffoldQueries(BaseModel):
    opt: ScaffoldOptions
    columns: dict[str, ColumnInfo]

    def scaffold(self):
        self.create_query_dir()
        self.create_find_query()
        self.create_find_one_query()
        self.create_save_query()
        self.create_delete_query()

    def create_find_query(self):
        mkfile(
            f"sql/{self.opt.snake_case}/find.sql",
            f"select *\nfrom {self.opt.snake_case}\n",
        )

    def create_find_one_query(self):
        mkfile(
            f"sql/{self.opt.snake_case}/find_one.sql",
            f"select *\nfrom {self.opt.snake_case}\nwhere id = {{id}}\n",
        )

    def create_save_query(self):

        content = (
            f"insert into {self.opt.snake_case}\n"  #
            f"values (\n"  #
            + ",\n".join(f"    {key}" for key in self.columns)
            + "\n)\n"  #
            "on conflict ({id}) do update set\n"  #
            + ",\n".join(f"    {key} = {{{key}}}" for key in self.columns)
            + "\nreturning "
            + ", ".join(self.columns)
        )
        print(content)
        print(",\n".join(f"    {key}" for key in self.columns))
        mkfile(f"sql/{self.opt.snake_case}/save.sql", content)

    def create_delete_query(self):
        mkfile(
            f"sql/{self.opt.snake_case}/delete.sql",
            f"delete from {self.opt.snake_case} where id = {{id}}",
        )

    def create_query_dir(self):
        mkdir(f"sql/{self.opt.snake_case}")


class ScaffoldModels(BaseModel):
    opt: ScaffoldOptions
    columns: dict[str, ColumnInfo]

    def scaffold(self):
        snake_case = self.opt.snake_case
        models = (
            "from src.database.models import BaseModel\n\n"
            f"class {self.opt.pascal_case}(BaseModel):\n"
            f"    {self.get_model_fields()}"
        )

        mkfile(f"./src/{snake_case}/models.py", models)

    def get_model_fields(self):
        if len(self.columns) == 0:
            return "    pass"

        return "    \n".join(
            f"{key}: {info.python_type.__name__}"
            for key, info in self.columns.items()
            if key != "id"
        )


class ScaffoldForms(BaseModel):
    opt: ScaffoldOptions
    columns: dict[str, ColumnInfo]


class ScaffoldCreator(BaseModel):
    opt: ScaffoldOptions
    schema_service: SchemaService

    async def scaffold(self):
        self.create_base_dir()
        self.create_init()

        if self.opt.controller:
            pass
            # self.create_controller()
        if self.opt.service:
            pass
            # self.create_service()
        if self.opt.models:
            await self.create_models()
        if self.opt.forms:
            self.create_forms()

    def create_forms(self):
        pass

    def create_base_dir(self):
        mkdir(f"./src/{self.opt.snake_case}")
        mkdir(f"./src/{self.opt.snake_case}/tests")

    async def create_models(self):
        columns = await self.schema_service.get_column_info(self.opt.snake_case)
        ScaffoldQueries(opt=self.opt, columns=columns).scaffold()
        ScaffoldModels(opt=self.opt, columns=columns).scaffold()

    def create_empty_controller(self):
        controller = (
            f"from fastapi import APIRouter\n\n"
            f'router = APIRouter(prefix="{self.snake_case}")'
        )

        mkfile(f"./src/{self.snake_case}/controller.py", controller)

    def create_init(self):
        imports = ", ".join(self._init_imports())
        mkfile(
            f"./src/{self.opt.snake_case}/__init__.py",
            imports and f"from . import {imports}",
        )

    def _init_imports(self):
        if self.opt.service:
            yield "service"
        if self.opt.controller:
            yield "controller"
        if self.opt.templates:
            yield "models"


async def main():

    options = ScaffoldOptions.from_args()
    cnn = await asyncpg.connect(os.environ["DATABASE_URL"])
    schema_service = SchemaService(cnn=Connection(cnn=cnn))
    creator = ScaffoldCreator(opt=options, schema_service=schema_service)
    await creator.scaffold()


if __name__ == "__main__":
    asyncio.run(main())

    # mkdir(f"./src/{options.snake_case}")

    # mkfile(f"./src/{snake_case}/controller.py", controller(snake_case))
    # mkfile(f"./src/{snake_case}/models.py", models(pascal_case))
    # mkfile(f"./src/{snake_case}/service.py", service(pascal_case))
    # mkfile(
    #     f"./src/{snake_case}/tests/test_{snake_case}_service.py",
    #     test_service(pascal_case),
    # )
    # mkfile(
    #     f"./src/$",
    # )


# mkdir "./src/$1"
# echo "" > ./src/$1/__init__.py
# echo "from fastapi import APIRouter\n\n\nrouter = APIRouter(prefix=\"$1\")\n" > ./src/$1/controller.py
# echo "from src.database.models import BaseModel\n\n\nclass $pascal_case(BaseModel):\n    pass" > ./src/$1/models.py
# echo "from pydantic import BaseModel, ConfigDict\n\nclass $(echo $pascal_case)Service(BaseModel):\n    model_config = ConfigDict(arbitrary_types_allowed=True)" > ./src/$1/service.py

# echo "import pytest\n\nfrom src.foo.service import FooService\n\n@pytest.fixture()\ndef foo_service():\n    return FooService()" > ./src/$1/tests/test_$(echo $1)_service.py


# mkdir ./src/$1/tests
# touch
# touch ./src/$1/tests/test_$(echo $1)_controller.py
# touch ./src/$1/tests/test_$(echo $1)_models.py
