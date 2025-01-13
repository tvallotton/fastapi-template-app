from typing import Annotated
from venv import logger

import asyncpg
from attr import dataclass
from fastapi import Depends, dependencies
from pgqueuer import AsyncpgDriver, Queries
from pydantic import BaseModel, ConfigDict, Field, SkipValidation

from src.database.service import get_pg_connection
from src.queue.job import BaseJob
from src.utils import dependency


def queue_service(cnn: Annotated[asyncpg.Connection, Depends(get_pg_connection)]):
    driver = AsyncpgDriver(cnn)
    return QueueService(queries=Queries(driver))


@dependency(queue_service)
class QueueService(BaseModel):
    queries: Annotated[Queries, SkipValidation]

    model_config = ConfigDict(arbitrary_types_allowed=True)

    async def push(self, job: BaseJob):
        json = job.model_dump_json()
        payload = bytes(json, "utf-8")
        return await self.queries.enqueue(job.entrypoint, payload=payload)
