import asyncpg
import pgqueuer
import pgqueuer.supervisor
from pgqueuer import AsyncpgPoolDriver, PgQueuer
from pydantic import BaseModel

from src.database.service import get_pg_connection, get_pg_pool
from src.environment import DATABASE_URL
from src.mail.consumer import MailConsumer
from src.queue.consumer import BaseConsumer
from src.queue.consumer_list import CONSUMERS
from src.utils import Injector


class QueueConfig(BaseModel):
    DATABASE_URL: str = DATABASE_URL


async def create_pgq(config: QueueConfig = QueueConfig()):
    pool = await asyncpg.create_pool(config.DATABASE_URL)
    driver = AsyncpgPoolDriver(pool)

    pgq = PgQueuer(driver)

    injector = Injector(overrides={get_pg_pool: lambda: pool})

    for consumer_type in CONSUMERS:
        consumer = injector.get(consumer_type)
        consumer.add_entrypoints(pgq)

    return pgq
