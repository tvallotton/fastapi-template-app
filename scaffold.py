#!python
import sys
from os import environ, mkdir

import asyncpg
from pydantic import BaseModel

from src.database.service import Connection
from src.schema.service import SchemaService

DATABASE_URL = environ["DATABASE_URL"]


async def get_columns(table_name):
    cnn = Connection(await asyncpg.connect(DATABASE_URL))

    cnn._column_names()
    "database/columns"


def mkfile(filename, output):
    with open(filename, "w") as f:
        f.write(output)


controller = (
    lambda prefix: f"""
from fastapi import APIRouter


router = APIRouter(prefix=\"{prefix}\")\n
"""
)

models = (
    lambda classname: f"""
from src.database.models import BaseModel


class {classname}(BaseModel):
    pass
"""
)

service = (
    lambda classname: f"""
from pydantic import BaseModel

from src.database.service import Connection


class {classname}Service(BaseModel):
    cnn: Connection
"""
)


test_service = (
    lambda classname: f"""
import pytest

@pytest.fixture()
def storage_service(cnn):
    return StorageService(cnn=cnn)
    
"""
)

test_models = (
    lambda classname: f"""
import pytest


"""
)


class ScaffoldOptions(BaseModel):
    snake_case: str
    models: bool
    controller: bool
    service: bool
    

    @property
    def pascal_case(self):
        return "".join(x.capitalize() for x in self.snake_case.lower().split("_"))
    

    @staticmethod
    def from_args():
        assert len(sys.argv) >= 2, "Excepted at least 1 argument"
        return ScaffoldOptions(
            snake_case=sys.argv[1],
            models="models" in sys.argv[1:],
            controller="controller" in sys.argv[1:],
            service="service" in sys.argv[1:],
            templates="templates" in sys.argv[1:],
        )


class ScaffoldCreator(BaseModel):
    opts: ScaffoldOptions
    schema_service: SchemaService

    def scaffold(self):
        self.create_base_dir()
        self.create_init()
        
        if self.opt.controller:
            self.create_controller()
        if self.service:
            self.create_service()
        if self.models:
            self.create_models()
            
        
    
    def create_base_dir(self):
        mkdir(f"./src/{self.snake_case}")
        mkdir(f"./src/{self.snake_case}/tests")
        
    
    async def create_models(self):
        models = (
            "from src.database.models import BaseModel\n\n"
            f"class {self.pascal_case}(BaseModel):\n"
            f"    {}"
        )
        mkdir(f"./src/{self.snake_case}/models.py", )
        

    
    
    def create_empty_controller(self):
        controller = (
            f"from fastapi import APIRouter\n\n"
            f"router = APIRouter(prefix=\"{self.snake_case}\")"
        )
        mkfile(f"./src/{self.snake_case}/controller.py", controller)
        
        
    def create_init(self):
        imports = ",".join(self._init_imports())
        mkfile(f"./src/{self.snake_case}/__init__.py", imports and f"from . import {imports}")
        
    def _init_imports(self):
        if self.service:
            yield "service"
        if self.controller:
            yield "controller"
        if self.templates:
            yield "models"
    
    


if __name__ == "__main__":

    options = ScaffoldOptions.from_args()

    mkdir(f"./src/{snake_case}")

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
