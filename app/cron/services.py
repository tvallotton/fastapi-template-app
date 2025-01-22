from typing import Callable, Coroutine

from apscheduler.triggers.cron import CronTrigger
from attr import dataclass
from pydantic import BaseModel, ConfigDict


@dataclass
class CronJob[T: "BaseCron"]:
    method: Callable[[T], Coroutine]
    trigger: CronTrigger


def cron[
    T: "BaseCron"
](
    year=None,
    month=None,
    day=None,
    week=None,
    day_of_week=None,
    hour=None,
    minute=None,
    second=None,
    start_date=None,
    end_date=None,
    timezone=None,
    jitter=None,
):

    def decorator(method: Callable[[T], Coroutine]) -> CronJob[T]:
        return CronJob(
            trigger=CronTrigger(
                year=year,
                month=month,
                day=day,
                week=week,
                day_of_week=day_of_week,
                hour=hour,
                minute=minute,
                second=second,
                start_date=start_date,
                end_date=end_date,
                timezone=timezone,
                jitter=jitter,
            ),
            method=method,
        )

    return decorator


class BaseCron(BaseModel):
    """
    Base class for defining cronjobs.

    Example:
    # at cron/lifespan.py
    CRON_CLASSES = [ExampleCron]

    # at example/cron.py
    class ExampleCron(BaseCron):
        example_service: ExampleService

        @cron(minute="0", hour="0")
        def run_at_mightnight():
            print("running at mightning")
    """

    model_config = ConfigDict(ignored_types=(CronJob,))

    @classmethod
    def jobs(cls):
        for job in vars(cls).values():
            if isinstance(job, CronJob):
                yield job
