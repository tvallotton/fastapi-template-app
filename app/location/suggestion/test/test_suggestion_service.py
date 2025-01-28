from app.database.factory import Factory
from app.database.repository import Repository
from app.location.place.factory import PlaceFactory
from app.location.suggestion.service import SuggestionService


async def test_suggestion(resolver):
    service = resolver.get(SuggestionService)
    factory = resolver.get(PlaceFactory)
    await factory.create(street="Abraham Lincoln", number="342")
    await factory.create(street="First street", number="634")

    suggestions = await service.suggest("lincoln 342")
    assert suggestions[0].number == "342"
