from src.user.model import User

pytest_plugins = ("pytest_asyncio",)


async def test_user_save(cnn, email="user@save.test"):
    user = await User(email=email).save(cnn)
    assert user is not None
    return user


async def test_find_user(cnn):

    email = "user@find.test"
    user = await test_user_save(cnn, email)

    user2 = await User.find_one(cnn, email=email)

    assert user2 is not None
    assert user2.id == user.id

    await user.delete(cnn)

    user3 = await User.find_one(cnn, email=email)
    assert user3 is None


async def test_delete_user(cnn):
    email = "user@delete.test"

    user = await test_user_save(cnn, email)
    await user.delete(cnn)
    assert not await User.find_one(cnn, email=email)
