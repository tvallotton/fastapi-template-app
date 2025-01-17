
from pydantic import BaseModel, Field


class MailOptions(BaseModel):
    template: str
    dest: str
    subject: str
    context: dict = Field(default_factory=dict)
    src: str | None = None
