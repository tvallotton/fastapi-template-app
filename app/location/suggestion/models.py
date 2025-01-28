from app.database.models import BaseModel


class Suggestion(BaseModel):
    id: int  # type: ignore
    address: str
    street: str
    number: str | None
    city_id: str
