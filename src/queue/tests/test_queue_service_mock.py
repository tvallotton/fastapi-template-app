from src.mail.dto import MailOptions
from src.mail.jobs import EmailJob
from src.queue.service import QueueService
from src.utils import Injector


async def test_send_email(injector: Injector):
    queue_service = injector.get(QueueService)
    await queue_service.push(
        EmailJob(options=MailOptions(template="signup", dest="foo@bar", subject="bar"))
    )
