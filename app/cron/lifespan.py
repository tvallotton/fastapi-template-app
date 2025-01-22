from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI

from app.cron.crons import CRON_CLASSES
from app.cron.services import CronJob
from app.database.service import get_pg_connection
from app.resolver import Resolver


def create_cronjob(app: FastAPI, cls: type, job: CronJob):
    async def run():
        async with app.state.db_pool.acquire() as cnn:
            resolver = Resolver(cached={get_pg_connection: cnn})
            cron_service = resolver.get(cls)
            await job.method(cron_service)

    return run


@asynccontextmanager
async def setup_cron(app: FastAPI):
    scheduler = AsyncIOScheduler()
    scheduler.start()

    for cron_class in CRON_CLASSES:
        for job in cron_class.jobs():
            job_func = create_cronjob(app, cron_class, job)
            scheduler.add_job(job_func, job.trigger)

    yield
    scheduler.shutdown()
