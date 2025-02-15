from app.database.repository import Repository
from app.user.factory import UserFactory
from app.user.models import User


async def test_user_factory(resolver):
    user_factory = resolver.get(UserFactory)
    user_repository = resolver.get(Repository[User])
    start = await user_repository.count()
    await user_factory.create()
    end = await user_repository.count()
    assert start + 1 == end
