from abc import ABC

from pydantic import BaseModel


class BaseJob(BaseModel, ABC):
    entrypoint: str
