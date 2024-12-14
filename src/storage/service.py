import hashlib
import os
from io import IOBase
from uuid import UUID

import aioboto3
from fastapi import UploadFile

from src.database.service import Connection
from src.storage.models import Storage

session = aioboto3.Session(
    aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID", "-"),
    aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY", "-"),
    aws_session_token="-",
)
endpoint_url = os.environ.get("AWS_S3_ENDPOINT_URL")

BUF_SIZE = 8 * 1028


class StorageService:
    def __init__(self, cnn: Connection):
        self.cnn = cnn

    async def presigned_url(self, storage: Storage):
        async with session.client("s3", endpoint_url=endpoint_url) as s3:
            params = {"Bucket": storage.bucket, "Key": storage.id.hex}
            return await s3.generate_presigned_url(
                "get_object",
                Params=params,
                ExpiresIn=60 * 60,
            )

    async def upload(self, bucket, file: IOBase) -> Storage:
        async with self.cnn.cnn.transaction():

            sha1 = self.sha1(file)
            storage = Storage(bucket=bucket, sha1=sha1)
            await storage.save(self.cnn)

            async with session.client("s3", endpoint_url=endpoint_url) as s3:
                await s3.upload_fileobj(file, bucket, storage.id.hex)

            return storage

    async def delete(self, storage: Storage):
        async with self.cnn.cnn.transaction():
            await storage.delete(self.cnn)
            async with session.client("s3", endpoint_url=endpoint_url) as s3:
                await s3.delete_object(Bucket=storage.bucket, Key=storage.id.hex)

    def sha1(self, file: UploadFile) -> bytes:
        file.seek(0)
        sha1 = hashlib.sha1()
        while True:
            data = file.read(BUF_SIZE)
            if not data:
                break
            sha1.update(data)
        file.seek(0)
        return sha1.digest()

    async def has_references(self, id: UUID):
        """
        Returns weather there are any foreign key references to this record.
        """
        foreign_keys = await self.cnn.fetch("database/foreign-keys-to", table="storage")

        for foreign_key in foreign_keys:
            count = await self.cnn.fetchrow(
                "storage/count-references", id=id, **foreign_key
            )

            if count["count"] != 0:
                return True
        return False
