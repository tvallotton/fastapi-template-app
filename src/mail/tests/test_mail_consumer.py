import asyncio
import os
from time import sleep

import httpx

from src.mail.dto import MailOptions
from src.mail.jobs import EmailJob
from src.queue.service import QueueService
from src.test_common import HTMLClient
from src.utils import Injector

client_ = httpx.AsyncClient()
MAILPIT_URL = os.environ["MAILPIT_URL"]


async def test_send_email(injector: Injector, client: HTMLClient):
    dest = "email@consumer.test"
    queue_service = injector.get(QueueService)
    await queue_service.push(
        EmailJob(options=MailOptions(template="test", dest=dest, subject="bar"))
    )
    await asyncio.sleep(0.05)
    client.read_email(dest)
    assert "hello world" in str(client.doc)
