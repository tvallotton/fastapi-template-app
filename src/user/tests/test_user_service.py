import pytest
from fastapi import BackgroundTasks
from pytest import fixture

from src.database.service import Connection
from src.mail.service import MailService
from src.test_common import HTMLClient
from src.user.models import User
from src.user.service import UserService


@pytest.fixture()
def user_service(cnn):
    return UserService(cnn=cnn, tasks=BackgroundTasks(), mail=MailService())


async def test_user_doesnt_exist(user_service: UserService):
    assert not await user_service.user_exists("non@existent.user")


async def test_user_exists(user_service: UserService, cnn: Connection):
    email = "user@does.exist"
    await User(email=email).save(cnn)
    assert await user_service.user_exists(email)


async def send_access_link(user_service: UserService, client: HTMLClient):
    email = "send@access.link"
    await user_service.send_access_link(email)
    client.read_email(email)
