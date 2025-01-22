from pydantic import BaseModel

from app.user.factory import UserFactory
from app.utils import dependency


@dependency()
class SeederService(BaseModel):
    user_factory: UserFactory

    async def seed(self):
        await self.seed_users()
        await self.seed_admin_user()

    async def seed_users(self):
        for _ in range(100):
            await self.user_factory.create()

    async def seed_admin_user(self):
        await self.user_factory.create(email="admin@domain.com", is_admin=True)
