from asyncio import sleep
from typing import Literal
from venv import logger

from src.mail.dto import MailOptions
from src.mail.jobs import EmailJob
from src.mail.service import MailService
from src.mail.tests.test_mail_service import mail_service
from src.queue.consumer import BaseConsumer
from src.queue.job import BaseJob


class MailConsumer(BaseConsumer):
    mail_service: MailService

    async def send_email(self, job: EmailJob):
        await self.mail_service.send(job.options)
