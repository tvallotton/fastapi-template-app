from app.database.models import BaseModel
from app.database.service import Connection


class User(BaseModel):
    email: str
    is_admin: bool = False

    def model_post_init(self, __context):
        self.email = self.email.lower()
