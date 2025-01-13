import os
from datetime import UTC, datetime, timedelta
from os import environ
from typing import Annotated

import jwt
from fastapi import BackgroundTasks, Depends
from pydantic import BaseModel, ConfigDict
from pydantic.dataclasses import dataclass

from src import mail
from src.database.repository import Repository
from src.database.service import Connection
from src.mail.dto import MailOptions
from src.mail.jobs import EmailJob
from src.mail.service import MailService
from src.queue.service import QueueService
from src.user.models import User
from src.utils import dependency

DOMAIN = environ["DOMAIN"]


@dependency()
class UserService(BaseModel):
    repository: Repository[User]
    queue: QueueService

    async def user_exists(self, email: str):
        user = await self.repository.find_one(email=email.lower())
        return user is not None

    async def send_access_link(self, email: str, next: str):
        print("/send to", email)
        token = self._create_token({"email": email}, timedelta(hours=1))
        context = {"link": f"{DOMAIN}/user/access?token={token}&next={next}"}
        opts = MailOptions(
            template="signup",
            dest=email,
            subject="Access link",
            context=context,
        )
        await self.queue.push(EmailJob(options=opts))

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
