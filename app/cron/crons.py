from app.cron.services import BaseCron
from app.storage.cron import StorageCron

CRON_CLASSES: list[type[BaseCron]] = [StorageCron]
