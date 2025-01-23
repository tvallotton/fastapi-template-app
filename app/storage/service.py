import hashlib
import os
from io import IOBase
from uuid import UUID

import aioboto3
from asyncpg import UniqueViolationError
from pydantic import BaseModel

from app.database.repository import Repository
from app.schema.service import SchemaService
from app.storage.models import Storage

session = aioboto3.Session(
    aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID", "-"),
    aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY", "-"),
    aws_session_token="-",
)
endpoint_url = os.environ.get("AWS_S3_ENDPOINT_URL")

BUF_SIZE = 8 * 1028


class StorageService(BaseModel):
    repository: Repository[Storage]
    schema_service: SchemaService

    async def presigned_url(self, storage: Storage):
        async with session.client("s3", endpoint_url=endpoint_url) as s3:  # type: ignore
            params = {"Bucket": storage.bucket, "Key": storage.id.hex}
            return await s3.generate_presigned_url(
                "get_object",
                Params=params,
                ExpiresIn=60 * 60,
            )

    async def upload(self, bucket, file: IOBase) -> Storage:
        async with self.repository.transaction():
            savepoint = await self.repository.savepoint()

            sha1 = self.sha1(file)
            storage = Storage(bucket=bucket, sha1=sha1)

            try:
                await self.repository.save(storage)

                async with session.client("s3", endpoint_url=endpoint_url) as s3:  # type: ignore
                    await s3.upload_fileobj(file, bucket, storage.id.hex)

            except UniqueViolationError:
                await self.repository.rollback(savepoint)
                storage = await self.repository.find_one(
                    "storage/find_duplicate", storage=storage
                )
                assert storage is not None
                return storage

            return storage

    async def delete(self, storage: Storage):
        async with self.repository.transaction():
            await self.repository.delete(storage.id)
            async with session.client("s3", endpoint_url=endpoint_url) as s3:  # type: ignore
                await s3.delete_object(Bucket=storage.bucket, Key=storage.id.hex)

    def sha1(self, file: IOBase) -> bytes:
        file.seek(0)
        sha1 = hashlib.sha1()
        while True:
            data = file.read(BUF_SIZE)
            if not data:
                break
            sha1.update(data)
        file.seek(0)
        return sha1.digest()

    async def delete_unreferenced_files(self):
        """Deletes all files which are not referenced by at least one record with a foreign key."""
        async with self.repository.transaction():
            async for storage in self.repository.find():
                if await self.has_references(storage):
                    continue
                else:
                    await self.delete(storage)

    async def has_references(self, storage: Storage):
        """
        Returns weather there are any foreign key references to this record.
        """
        references = await self.schema_service.get_table_references("storage")

        for column in references:
            for reference in references[column]:
                count = await self.repository.count(
                    "storage/count-references", id=storage.id, **reference.model_dump()
                )
                if count != 0:
                    return True

        return False
