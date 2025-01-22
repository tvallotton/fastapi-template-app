import pytest

from app.database.repository import Repository
from app.test_common import HTMLClient
from app.user.models import User
from app.user.service import UserService


@pytest.fixture(scope="function")
def user_service(resolver):
    return resolver.get(UserService)


@pytest.fixture(scope="function")
def user_repository(resolver):
    return resolver.get(Repository[User])


async def test_user_doesnt_exist(user_service: UserService):
    assert not await user_service.user_exists("non@existent.user")


async def test_user_exists(
    user_service: UserService, user_repository: Repository[User]
):
    email = "user@does.exist"
    user = User(email=email)
    await user_repository.save(user)
    assert await user_service.user_exists(email)


async def send_access_link(user_service: UserService, client: HTMLClient):
    email = "send@access.link"
    await user_service.send_access_link(email, "/")
    client.read_email(email)
