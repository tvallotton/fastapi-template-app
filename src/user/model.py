from src.database.models import BaseModel
from src.database import Connection


class User(BaseModel):
    email: str
    is_admin: bool = False

    def model_post_init(self, __context):
        self.email = self.email.lower()

    @classmethod
    def fake(cls, cnn: Connection, **data):
        from src.faker import fake

        data.setdefault("email", fake.unique.ascii_email())
        return super(User, cls).fake(cnn, **data)
