import asyncio

from src.database.service import transaction
from src.user.model import User


async def seed_users():
    async with transaction() as cnn:
        for _ in range(10_000):
            await User.fake(cnn)


async def seed_admin_user():
    async with transaction() as cnn:
        user = await User.find_one(cnn, email="admin@user")
        if user:
            return
        await User.fake(cnn, email="admin@user", is_admin=True)


async def seed():
    await asyncio.gather(seed_users(), seed_admin_user())


asyncio.run(seed())
