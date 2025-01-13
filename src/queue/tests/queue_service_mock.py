from asyncio import iscoroutinefunction
from inspect import iscoroutine
from typing import Any, Callable

from pgqueuer import Job, Queries
from pydantic import Field
from traitlets import default

from src.database.models import BaseModel
from src.queue.consumer_list import CONSUMERS
from src.queue.job import BaseJob
from src.queue.service import QueueService
from src.utils import Injector, dependency


@dependency()
class QueueServiceMock(QueueService):
    injector: Injector
    queries: None = None

    async def push(self, job: BaseJob):
        found = False
        for consumer_type in CONSUMERS:
            consumer = self.injector.get(consumer_type)
            for adapter in consumer.get_adapters():
                if adapter.get_entrypoint() == job.entrypoint:
                    if iscoroutinefunction(adapter.handler):
                        await adapter.handler(job)
                    else:
                        adapter.handler(job)
                    found = True
                    break
        assert found, f"No entrypoint for {job.entrypoint} was found"
        return []
