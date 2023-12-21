import logging

from mmorpg_site import settings

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django.utils import timezone
from datetime import timedelta
from board.models import Advertisement
from django.contrib.auth.models import User
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


# наша задача по выводу текста на экран
def my_job():
    today = timezone.now()
    list_week_advs = list(Advertisement.objects.filter(time_create__gte=today - timedelta(days=7)))
    if list_week_advs:
        for user in User.objects.filter():
            list_advs = ''
            for advs in list_week_advs:
                list_advs += f'\n{advs.title}\nhttp://127.0.0.1:8000/post/{advs.id}'
            send_mail(
                subject=f'MMORPG_site: Объявления за прошлую неделю.',
                message=f'Добрый день, {user.username}! Ознакомьтесь с новыми объявлениями на нашем сайте, '
                        f'которые появились за прошедшие 7 дней:\n{list_advs}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email, ],
            )


# функция, которая будет удалять неактуальные задачи
def delete_old_job_executions(max_age=604_800):
    """This job deletes all apscheduler job executions older than `max_age` from the database."""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs apscheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # добавляем работу нашему задачнику
        scheduler.add_job(
            my_job,
            trigger=CronTrigger(day_of_week="mon", hour="08", minute="00"),
            # То же, что и интервал, но задача тригера таким образом более понятна django
            id="my_job",  # уникальный айди
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'my_job'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),
            # Каждую неделю будут удаляться старые задачи, которые либо не удалось выполнить, либо уже выполнять не надо.
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info(
            "Added weekly job: 'delete_old_job_executions'."
        )

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")