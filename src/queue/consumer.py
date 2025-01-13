import inspect
import json
import logging
from abc import ABC
from ast import Call
from enum import StrEnum
from typing import Any, Callable, TypedDict

from aiohttp import payload_type
from pgqueuer import Job, PgQueuer
from pydantic import BaseModel, Field
from pytest import console_main
from traitlets import default

from faker import Generator
from src.environment import DATABASE_URL
from src.queue.job import BaseJob


class BaseConsumer(BaseModel, ABC):

    def add_entrypoints(self, pgq: PgQueuer):
        for adapter in self.get_adapters():
            adapted_handler = adapter.adapt_handler()
            entrypoint = adapter.get_entrypoint()
            pgq.entrypoint(entrypoint)(adapted_handler)

    def get_adapters(self):
        methods = self.get_methods()
        for method in methods:
            handler: Callable[[BaseJob], Any] = getattr(self, method)
            adapter = HandlerAdapter(handler=handler)
            yield adapter

    @classmethod
    def get_methods(cls) -> list[str]:
        # Get all attributes of the class
        all_methods = dir(cls)

        # Filter methods that are defined in the class itself
        defined_methods = [
            method
            for method in all_methods
            if callable(getattr(cls, method))
            and not method.startswith("__")
            and method in cls.__dict__
        ]

        return defined_methods


class HandlerAdapter(BaseModel):
    handler: Callable[[BaseJob], Any]

    def adapt_handler(self):

        def sync_adapted_handler(pgq_job: Job):
            job = self.transform_job(pgq_job)
            return self.handler(job)

        async def async_adapted_handler(pgq_job: Job):
            job = self.transform_job(pgq_job)
            return await self.handler(job)

        if inspect.iscoroutinefunction(self.handler):
            return async_adapted_handler
        else:
            return sync_adapted_handler

    def transform_job(self, pgq_job: Job) -> BaseJob:
        job_class = self.get_job_class()
        payload_bytes = pgq_job.payload or b"{}"
        payload = json.loads(str(payload_bytes, "utf-8"))
        job = job_class(**payload)
        return job

    def get_job_class(self) -> type[BaseJob]:
        type_annotations = self.handler.__annotations__.values()
        return next(iter(type_annotations))

    def get_entrypoint(self) -> str:
        schema = self.get_job_class().model_json_schema()
        return schema["properties"]["entrypoint"]["default"]
