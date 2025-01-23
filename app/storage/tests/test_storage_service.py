import io
from uuid import UUID

import httpx
import pytest
import pytest_asyncio

from app.database.factory import Factory
from app.database.models import BaseModel
from app.database.service import Connection
from app.storage.service import StorageService


@pytest.fixture()
def storage_service(resolver):
    return resolver.get(StorageService)


class ReferenceTable(BaseModel):
    storage_id: UUID

    @classmethod
    def model_dir(cls):
        return "storage/test"


@pytest_asyncio.fixture(loop_scope="session")
async def reference_table_factory(resolver):
    connection = resolver.get(Connection)
    await connection.execute("storage/test/create_table")
    yield resolver.get(Factory[ReferenceTable])
    await connection.execute("storage/test/drop_table")


async def test_upload_new(storage_service: StorageService):
    buffer = io.BytesIO(b"hello world")
    await storage_service.upload("test", buffer)


async def test_upload_duplicate(storage_service: StorageService):
    buffer = io.BytesIO(b"duplicate buffer")
    await storage_service.upload("test", buffer)

    async with storage_service.repository.transaction():
        start = await storage_service.repository.count()
        await storage_service.upload("test", buffer)

        end = await storage_service.repository.count()
        assert (
            start == end
        ), "Duplicate control should prevent the file from being uploaded again"


async def test_presigned_url(storage_service: StorageService):
    message = "presigned buffer"
    buffer = io.BytesIO(bytes(message, "utf-8"))
    storage = await storage_service.upload("test", buffer)
    url = await storage_service.presigned_url(storage)
    assert message in httpx.get(url).text


async def test_delete(storage_service: StorageService):
    buffer = io.BytesIO(b"message to delete")
    storage = await storage_service.upload("test", buffer)

    url = await storage_service.presigned_url(storage)

    await storage_service.delete(storage)
    assert httpx.get(url).status_code == 404


async def test_has_no_references(storage_service: StorageService):
    buffer = io.BytesIO(b"message without references")
    storage = await storage_service.upload("test", buffer)
    assert not await storage_service.has_references(storage)


async def test_has_references(
    storage_service: StorageService,
    reference_table_factory: Factory[ReferenceTable],
):
    buffer = io.BytesIO(b"message with references")
    storage = await storage_service.upload("test", buffer)
    await reference_table_factory.create(storage_id=storage.id)
    assert await storage_service.has_references(storage)


async def test_delete_unreferenced_files(storage_service: StorageService):
    buffer = io.BytesIO(b"message to delete")
    storage = await storage_service.upload("test", buffer)
    await storage_service.delete_unreferenced_files()

    assert await storage_service.repository.find_one(id=storage.id) is None


async def test_not_delete_referenced_files(
    storage_service: StorageService,
    reference_table_factory: Factory[ReferenceTable],
):
    buffer = io.BytesIO(b"message to keep")
    storage = await storage_service.upload("test", buffer)

    await reference_table_factory.create(storage_id=storage.id)
    await storage_service.delete_unreferenced_files()
    assert await storage_service.repository.find_one(id=storage.id) is not None
