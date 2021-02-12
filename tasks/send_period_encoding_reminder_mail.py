from datetime import timedelta

from django.utils.datetime_safe import date

from backoffice.celery import app as celery_app
from internship.models.period import Period
from internship.utils.mails.mails_management import send_internship_period_encoding_reminder

DAYS_BEFORE = 15


@celery_app.task
def run() -> dict:
    active_period = Period.active.first()
    trigger_date = active_period.date_end - timedelta(days=DAYS_BEFORE)
    if date.today() >= trigger_date and not active_period.sent_reminder_mail:
        send_internship_period_encoding_reminder(active_period)
    return {}
