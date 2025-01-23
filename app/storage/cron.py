from calendar import weekday

from app.cron.services import BaseCron, cron
from app.storage.service import StorageService


class StorageCron(BaseCron):
    storage_service: StorageService

    @cron(day_of_week="0")
    async def delete_unreferenced_files(self):
        """Delete files which are not referenced by any other record once a week."""
        await self.storage_service.delete_unreferenced_files()
