import os
from datetime import UTC, datetime, timedelta
from os import environ

import jwt
from fastapi import BackgroundTasks
from pydantic import BaseModel, ConfigDict

from app.database.repository import Repository
from app.mail.dto import MailOptions
from app.mail.service import MailService
from app.user.exceptions import (
    EmailAlreadyRegisteredException,
    UnregisteredEmailException,
)
from app.user.models import User
from app.utils import dependency

DOMAIN = environ["DOMAIN"]


@dependency()
class UserService(BaseModel):
    repository: Repository[User]
    background_tasks: BackgroundTasks
    mail_service: MailService

    model_config = ConfigDict(arbitrary_types_allowed=True)

    async def send_login_link(self, email: str, next: str):
        if not await self.user_exists(email):
            raise UnregisteredEmailException()

        await self.send_access_link(email, next)

    async def send_signup_link(self, email: str, next: str):
        if await self.user_exists(email):
            raise EmailAlreadyRegisteredException()
        return self.send_access_link(email, next)

    async def user_exists(self, email: str):
        user = await self.repository.find_one(email=email.lower())
        return user is not None

    async def send_access_link(self, email: str, next: str):
        token = self._create_token({"email": email}, timedelta(hours=1))
        context = {"link": f"{DOMAIN}/user/access?token={token}&next={next}"}
        opts = MailOptions(
            template="signup",
            dest=email,
            subject="Access link",
            context=context,
        )

        self.background_tasks.add_task(self.mail_service.send, opts)

    async def verify_token(self, token: str):
        payload = jwt.decode(token, os.environ["JWT_SECRET_KEY"], algorithms=["HS256"])

        user = await self.repository.find_one(email=payload["email"])

        if user is None:
            user = User(**payload)
            await self.repository.save(user)

        return self.create_token(user)

    def create_token(self, user: User, exp=timedelta(days=2)):
        return self._create_token(
            {"user_id": user.id.hex, "is_admin": user.is_admin}, exp
        )

    def _create_token(self, payload: dict, exp=timedelta(days=2)):
        payload["exp"] = datetime.now(UTC) + exp
        return jwt.encode(payload, environ["JWT_SECRET_KEY"], algorithm="HS256")
        return jwt.encode(payload, environ["JWT_SECRET_KEY"], algorithm="HS256")
