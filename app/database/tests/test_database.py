import pytest
import pytest_asyncio

from app.database.factory import Factory
from app.database.models import BaseModel
from app.database.repository import Repository
from app.database.service import Connection

pytest_plugins = ("pytest_asyncio",)


async def test_fetchrow(cnn: Connection):
    value = "fetch_one"
    column_name = "bar"
    row = await cnn.fetchrow("database/test", value=value, column_name=column_name)
    assert row is not None
    assert row[column_name] == value


async def test_fetch(cnn: Connection):
    value = "fetch_rows"
    column_name = "bar"
    rows = await cnn.fetch("database/test", value=value, column_name=column_name)
    assert len(rows) == 1
    assert rows[0][column_name] == value


async def test_ident_sql_injection(cnn: Connection):

    value = "foo"
    column_name = '"bar", 1 as baz'
    row = await cnn.fetchrow("database/test", value=value, column_name=column_name)
    assert row is not None
    assert "baz" not in row.keys()
    assert column_name in row.keys()


async def test_expr_sql_injection(cnn: Connection):

    value = "'foo' as baz, 1"
    column_name = "bar"
    row = await cnn.fetchrow("database/test", value=value, column_name=column_name)
    assert row is not None
    assert "foo" not in row.values()
    assert value in row.values()


class Foo(BaseModel):
    field: str

    @classmethod
    def model_dir(cls):
        return "database/test_table"


@pytest_asyncio.fixture(loop_scope="session", scope="function")
async def test_table(cnn: Connection):
    await cnn.execute("database/test_table/drop")
    await cnn.execute("database/test_table/create_table")
    yield
    await cnn.execute("database/test_table/drop")


@pytest.fixture()
def foo_repository(resolver, test_table):
    return resolver.get(Repository[Foo])


@pytest.fixture()
def foo_factory(resolver, test_table):
    return resolver.get(Factory[Foo])


async def test_field_access(cnn: Connection):
    field = "field"
    record = await cnn.fetchrow("database/test_field_access", value=Foo(field=field))
    assert record is not None
    assert record["field"] == field


async def test_model_crud(cnn: Connection, foo_repository: Repository[Foo]):

    record = await foo_repository.save(Foo(field="foo"))
    record2 = await foo_repository.find_one(id=record.id)

    assert record == record2
    await foo_repository.delete(record.id)

    record3 = await foo_repository.find_one(id=record.id)

    assert record3 is None


async def test_foo_factory(foo_repository: Repository[Foo], foo_factory: Factory[Foo]):
    start = await foo_repository.count()
    await foo_factory.create()
    end = await foo_repository.count()
    assert start + 1 == end
