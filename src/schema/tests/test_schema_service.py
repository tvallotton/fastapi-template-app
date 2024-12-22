import pytest

from src.schema.service import SchemaService


@pytest.fixture()
def schema_service(cnn):
    return SchemaService(cnn=cnn)


async def test_user_has_history(schema_service: SchemaService):
    assert await schema_service.has_history("user")


async def test_user_history_doesnt_have_history(schema_service: SchemaService):
    assert not await schema_service.has_history("user_history")


async def test_user_columns(schema_service: SchemaService):
    columns = await schema_service.get_column_info("user")
    assert not columns["id"].is_required
    assert columns["email"].is_required
