import pytest

from app.database.repository import Repository
from app.user.models import User


@pytest.fixture(scope="function")
def repository(resolver):
    return resolver.get(Repository[User])


async def test_user_save(repository, email="user@save.test"):
    user = await repository.save(User(email=email))
    assert user is not None
    return user


async def test_find_user(repository: Repository[User]):
    email = "user@find.test"
    user = await test_user_save(repository, email)

    user2 = await repository.find_one(email=email)

    assert user2 is not None
    assert user2.id == user.id

    await repository.delete(user.id)

    user3 = await repository.find_one(email=email)
    assert user3 is None


async def test_delete_user(repository: Repository[User]):
    email = "user@delete.test"

    user = await test_user_save(repository, email)
    await repository.delete(user.id)
    assert not await repository.find_one(email=email)
