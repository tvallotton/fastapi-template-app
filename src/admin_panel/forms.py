from pydantic import BaseModel


class AdminQuery(BaseModel):
    offset: int = 0
    limit: int = 0
    order_by: str | None = None
    filters: dict[str, str] | None = None
