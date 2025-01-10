import io

import httpx
import pytest
from asyncpg import UniqueViolationError
from fastapi import UploadFile

from src import storage
from src.database.repository import Repository
from src.database.service import Connection
from src.storage.models import Storage
from src.storage.service import StorageService


@pytest.fixture()
def storage_service(injector):
    return injector.get(StorageService)


@pytest.mark.filterwarnings("ignore:datetime.datetime.utcnow")
async def test_upload_new(storage_service: StorageService):
    buffer = io.BytesIO(b"hello world")
    await storage_service.upload("test", buffer)


@pytest.mark.filterwarnings("ignore:datetime.datetime.utcnow")
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


@pytest.mark.filterwarnings("ignore:datetime.datetime.utcnow")
async def test_presigned_url(storage_service: StorageService):
    message = "presigned buffer"
    buffer = io.BytesIO(bytes(message, "utf-8"))
    storage = await storage_service.upload("test", buffer)
    url = await storage_service.presigned_url(storage)
    assert message in httpx.get(url).text


@pytest.mark.filterwarnings("ignore:datetime.datetime.utcnow")
async def test_delete(storage_service: StorageService):
    buffer = io.BytesIO(b"message to delete")
    storage = await storage_service.upload("test", buffer)

    url = await storage_service.presigned_url(storage)

    await storage_service.delete(storage)
    assert httpx.get(url).status_code == 404
