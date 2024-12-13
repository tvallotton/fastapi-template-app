import asyncio
import os

import asyncpg
import dotenv

from src.database.service import Connection
from src.user.model import User

dotenv.load_dotenv()


async def seed():
    pg_conneciton = await asyncpg.connect(os.environ["DATABASE_URL"])
    cnn = Connection(pg_conneciton)

    await users(cnn)
    await admin_user(cnn)


async def users(cnn):
    for _ in range(500):
        await User.fake(cnn)


async def admin_user(cnn):
    await User(email="admin@pp.cl", is_admin=True).save(cnn)


if __name__ == "__main__":
    asyncio.run(seed())
