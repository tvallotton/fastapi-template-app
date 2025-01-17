from pydantic import BaseModel

from app import create_app
from app.database.repository import Repository
from app.user.models import User
from app.utils import dependency


@dependency()
class SeederService(BaseModel):
    user_repository: Repository[User]

    async def seed(self):
        await self.seed_users()
        await self.seed_admin_user()

    async def seed_users(self):
        for _ in range(100):
            await self.user_repository.fake()

    async def seed_admin_user(self):
        user = User(email="admin@domain.com", is_admin=True)
        await self.user_repository.save(user)
