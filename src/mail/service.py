import asyncio
import ssl
from dataclasses import dataclass
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os import environ
from typing import Annotated, Unpack

import aiosmtplib
from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict

from src.environment import PROD_ENV
from src.mail.dto import MailOptions
from src.templating import templates
from src.utils import dependency

load_dotenv(".env.development")
context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)


SMTP_HOST = environ["SMTP_HOST"]
SMTP_PORT = int(environ["SMTP_PORT"])
SMTP_USER = environ["SMTP_USER"]
SMTP_PASS = environ["SMTP_PASS"]
SMTP_START_TLS = environ["SMTP_START_TLS"] == "true"
SMTP_USE_TLS = environ["SMTP_USE_TLS"] == "true"
IS_SAFE = SMTP_START_TLS or SMTP_USE_TLS

assert IS_SAFE or not PROD_ENV


@dependency()
class MailService(BaseModel):

    def __init__(self):
        super().__init__()
        self._lock = asyncio.Lock()
        self._server = aiosmtplib.SMTP(
            hostname=SMTP_HOST,
            port=SMTP_PORT,
            password=SMTP_USER,
            username=SMTP_PASS,
            tls_context=context,
            start_tls=SMTP_START_TLS,
            use_tls=SMTP_USE_TLS,
        )

    model_config = ConfigDict(arbitrary_types_allowed=True)

    async def send(self, opts: MailOptions):
        src = opts.src or SMTP_USER
        message = MIMEMultipart("alternative")
        message["From"] = src
        message["To"] = opts.dest
        message["Subject"] = opts.subject

        html = templates.get_template(f"email/{opts.template}.html").render(
            opts.context
        )
        html = MIMEText(html, "html")

        message.attach(html)

        async with self._lock:
            async with self._server:
                await self._server.sendmail(src, opts.dest, message.as_bytes())
