from celery import Celery
from celery.decorators import task
from celery.utils.log import get_task_logger
from .models import Task
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q
from celery.task.schedules import crontab
from celery.decorators import periodic_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@periodic_task(
    run_every=(crontab(minute='*/5')),
    name="task_send_warning_email",
    ignore_result=True
)
def send_warning_email_task():
    """Use celery to send a warning email once the due date of the task is
       within 1 day.
    """
    for email_task in Task.objects.all().filter(Q(user_id=1)):
        if((timezone.now() - email_task.due_date) < 86400) and (email_task.time_delta > 86400):
            if not email_task.notified:
                email_task.notified = True

                """Find the user based on task ID"""
                user = User.objects.all().filter(id=email_task.user_id)

                if user.email_alerts:
                    """send an email with the task name, due date, and last
                       acknowledged send_mail(subject, message, from_email,
                       to_list, fail_silently=True)
                    """
                    subject = "{}, '{}' is due soon, at {}".format(
                        user.name,
                        email_task.name,
                        email_task.due_date
                    )
                    message = 'The task was last acknowledged at {}.  Log in to your account to see the task and ' \
                              'acknowledge it.<nrhttp://www.AwhileSince.com/profile/'.format(email_task.last_acknowledged)
                    from_email = settings.EMAIL_HOST_USER
                    to_list = [user.email, settings.EMAIL_HOST_USER]

                    send_mail(subject, message, from_email, to_list, fail_silently=False)

                    logger.info("Sent warning email about task: {} to user: {} at address: {}".format(email_task.name, user.name, user.email))

