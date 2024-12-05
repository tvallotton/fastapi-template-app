import ssl
from dataclasses import dataclass
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os import environ
from typing import Annotated

from dotenv import load_dotenv
from fastapi import Depends

load_dotenv(".env.development")
import aiosmtplib

from src.templating import templates

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


@dataclass
class MailService:

    async def send(self, template: str, dest: str, subject: str, context: dict = {}):
        src = environ["SMTP_USER"]
        message = MIMEMultipart("alternative")
        message["From"] = src
        message["To"] = dest
        message["Subject"] = subject

        html = templates.get_template(f"email/{template}.html").render(context)
        html = MIMEText(html, "html")

        message.attach(html)

        async with server:
            return await server.sendmail(src, dest, message.as_bytes())


MailService = Annotated[MailService, Depends(MailService)]
