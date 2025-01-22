from pydantic import BaseModel

from app.database.factory import Factory
from app.user.models import User
from app.utils import dependency


@dependency()
class UserFactory(BaseModel):
    factory: Factory[User]

    def create(self, **data):
        from app.fake import fake

        data.setdefault("email", fake.unique.ascii_email())
        return self.factory.create(**data)
