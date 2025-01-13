import os
from re import sub

import httpx
import pytest

from src import mail
from src.mail.dto import MailOptions
from src.mail.service import MailService
from src.test_common import HTMLClient


@pytest.fixture()
def mail_service():
    return MailService()


async def test_send_email(mail_service: MailService, client: HTMLClient):
    dest = "email.service@test"

    opts = MailOptions(
        template="test",
        dest=dest,
        subject="greetings",
    )

    await mail_service.send(opts)
    client.read_email(dest)
    assert "hello world" in str(client.doc)
