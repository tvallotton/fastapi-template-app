from datetime import datetime, timedelta
from enum import StrEnum
from uuid import UUID

from src.database.models import BaseModel


class PgQueuerStatus(StrEnum):
    PICKED = "picked"
    QUEUED = "queued"


class PgQueuer(BaseModel):
    id: int  # type: ignore
    priority: int
    queue_manager_id: UUID
    created: datetime
    updated: datetime
    heartbeat: datetime
    execute_after: datetime
    status: PgQueuerStatus
    entrypoint: str
    payload: bytes

    @classmethod
    def table_name(cls):
        return "pgqueuer"


class PgQueuerSchedules(BaseModel):
    id: int  # type: ignore
    expression: str
    entrypoint: str
    heartbeat: datetime
    created: datetime
    updated: datetime
    next_run: datetime
    last_run: datetime
    status: PgQueuerStatus


class PgQueuerStatisticsStatus(StrEnum):
    EXCEPTION = "exception"
    SUCESSFUL = "successful"
    CANCELLED = "canceled"


class PgQueuerStatistics(BaseModel):
    id: int  # type: ignore
    created: datetime
    count: int
    priority: int
    time_in_queue: timedelta
    status: PgQueuerStatisticsStatus
    entrypoint: str

    @classmethod
    def table_name(cls):
        return "pgqueuer_statistics"
