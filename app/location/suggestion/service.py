from pydantic import BaseModel

from app.database.repository import Repository
from app.location.suggestion.models import Suggestion


class SuggestionService(BaseModel):
    suggestion_repository: Repository[Suggestion]

    async def suggest(self, address: str):
        async with self.suggestion_repository.transaction():
            suggestions = self.suggestion_repository.find(
                "by_similarity", address=address
            )
            return [suggestion async for suggestion in suggestions]
