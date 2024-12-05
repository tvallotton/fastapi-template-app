import io

import httpx
import pytest
from asyncpg import UniqueViolationError
from fastapi import UploadFile

from src import storage
from src.database import Connection
from src.storage.service import StorageService


@pytest.fixture()
def storage_service(cnn):
    return StorageService(cnn=cnn)


@pytest.mark.filterwarnings("ignore:datetime.datetime.utcnow")
async def test_upload(storage_service: StorageService):
    buffer = io.BytesIO(b"hello world")
    await storage_service.upload("test", buffer)


@pytest.mark.filterwarnings("ignore:datetime.datetime.utcnow")
async def test_upload_duplicate(storage_service: StorageService):
    buffer = io.BytesIO(b"duplicate buffer")
    await storage_service.upload("test", buffer)
    with pytest.raises(UniqueViolationError):
        await storage_service.upload("test", buffer)


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


@pytest.mark.filterwarnings("ignore:datetime.datetime.utcnow")
async def test_has_references(storage_service: StorageService, cnn: Connection):

    await cnn.inline.execute(
        """
        create table if not exists testing_table_storage_fk  (
            id uuid primary key default gen_random_uuid(), 
            storage_id uuid references storage(id)
        );
        insert into storage (id, bucket, sha1) values ('b0ac6986-c14b-4b9c-9da4-8403b2bb94ab', 'test', '\\x00');
        insert into storage (id, bucket, sha1) values ('d5d88cc1-2aa8-432b-949c-b8e0e6432cb3', 'test', '\\x01');
        
        insert into testing_table_storage_fk (storage_id) values ('d5d88cc1-2aa8-432b-949c-b8e0e6432cb3');

    """
    )

    assert await storage_service.has_references("d5d88cc1-2aa8-432b-949c-b8e0e6432cb3")
    assert not await storage_service.has_references(
        "b0ac6986-c14b-4b9c-9da4-8403b2bb94ab"
    )
