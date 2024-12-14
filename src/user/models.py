from src.database.models import BaseModel
from src.database.service import Connection


class User(BaseModel):
    email: str
    is_admin: bool = False

    def model_post_init(self, __context):
        self.email = self.email.lower()

    @classmethod
    async def fake(cls, cnn: Connection, **data):
        from src.faker import fake

        data.setdefault("email", fake.unique.ascii_email())
        return await super(User, cls).fake(cnn, **data)
