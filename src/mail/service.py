import ssl
from dataclasses import dataclass
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os import environ
from typing import Annotated, Unpack

import aiosmtplib
from dotenv import load_dotenv
from fastapi import Depends
from pydantic import BaseModel

from src.mail.dto import MailOptions
from src.templating import templates
from src.utils import dependency

load_dotenv(".env.development")
context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)


server = aiosmtplib.SMTP(
    hostname=environ["SMTP_HOST"],
    port=int(environ["SMTP_PORT"]),
    password=environ["SMTP_USER"],
    username=environ["SMTP_PASS"],
    tls_context=context,
    start_tls=environ["SMTP_START_TLS"] == "true",
    use_tls=environ["SMTP_USE_TLS"] == "true",
)

IS_SAFE = environ["SMTP_START_TLS"] == "true" or environ["SMTP_USE_TLS"] == "true"

assert IS_SAFE or environ["ENV"] != "prod"


@dependency()
class MailService(BaseModel):

    async def send(self, opts: MailOptions):
        src = opts.src or environ["SMTP_USER"]
        message = MIMEMultipart("alternative")
        message["From"] = src
        message["To"] = opts.dest
        message["Subject"] = opts.subject

        html = templates.get_template(f"email/{opts.template}.html").render(
            opts.context
        )
        html = MIMEText(html, "html")

        message.attach(html)

        async with server:
            await server.sendmail(src, opts.dest, message.as_bytes())
