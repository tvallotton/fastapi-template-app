from src.mail.consumer import MailConsumer
from src.queue.consumer import BaseConsumer

CONSUMERS: list[type[BaseConsumer]] = [MailConsumer]
