from pytest import fixture
import pytest
from src.database.service import Connection
from src.user.model import User
from src.user.service import UserService
from fastapi import BackgroundTasks

from src.test_common import HTMLClient


@pytest.fixture()
def user_service(cnn):
    return UserService(cnn=cnn, tasks=BackgroundTasks())


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
