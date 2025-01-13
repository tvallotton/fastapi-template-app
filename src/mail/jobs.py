from typing import Literal

from src.mail.dto import MailOptions
from src.queue.job import BaseJob


class EmailJob(BaseJob):
    options: MailOptions
    entrypoint: Literal["send_email"] = "send_email"
