import pytest

from app.mail.dto import MailOptions
from app.mail.service import MailService
from app.test_common import HTMLClient


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
    assert "hello world" in repr(client.doc)
