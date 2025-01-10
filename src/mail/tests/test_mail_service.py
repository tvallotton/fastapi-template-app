import os
from re import sub

import httpx
import pytest

from src import mail
from src.mail.dto import MailOptions
from src.mail.service import MailService

client = httpx.AsyncClient()

MAILPIT_URL = os.environ["MAILPIT_URL"]


@pytest.fixture()
def mail_service():
    return MailService()


async def test_send_email(mail_service: MailService):
    dest = "email.service@test"

    opts = MailOptions(
        template="test",
        dest=dest,
        subject="greetings",
    )

    await mail_service.send(opts)

    response = await client.get(f"{MAILPIT_URL}/search", params={"query": dest})

    id = response.json()["messages"][0]["ID"]

    response = await client.get(f"{MAILPIT_URL}/message/{id}")

    assert "hello world" in response.json()["HTML"]
