from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from os import environ
import os
from typing import Annotated
from fastapi import BackgroundTasks, Depends

import jwt

from src import mail
from src.database import Connection
from src.user.model import User

DOMAIN = environ["DOMAIN"]


@dataclass
class UserService:
    cnn: Connection
    tasks: BackgroundTasks

    async def user_exists(self, email: str):
        user = await User.find_one(self.cnn, email=email.lower())
        return user is not None

    async def send_access_link(self, email: str, next: str):
        token = self._create_token({"email": email}, timedelta(hours=1))
        context = {"link": f"{DOMAIN}/user/access?token={token}&next={next}"}
        self.tasks.add_task(mail.service.send, "signup", email, "Access link", context)

    async def verify_token(self, token: str):
        payload = jwt.decode(token, os.environ["JWT_SECRET_KEY"], algorithms=["HS256"])

        user = await User.find_one(self.cnn, email=payload["email"])

        if user is None:
            user = User(**payload)
            await user.save(self.cnn)

        return self.create_token(user)

    def create_token(self, user: User, exp=timedelta(days=2)):
        return self._create_token(
            {"user_id": user.id.hex, "is_admin": user.is_admin}, exp
        )

    def _create_token(self, payload: dict, exp=timedelta(days=2)):
        payload["exp"] = datetime.now(UTC) + exp
        return jwt.encode(payload, environ["JWT_SECRET_KEY"], algorithm="HS256")


UserService = Annotated[UserService, Depends()]
