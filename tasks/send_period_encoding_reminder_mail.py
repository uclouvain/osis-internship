from datetime import timedelta

from django.utils.datetime_safe import date

from backoffice.celery import app as celery_app
from internship.models.period import Period
from internship.utils.mails.mails_management import send_internship_period_encoding_reminder

DAYS_BEFORE = 15


@celery_app.task
def run() -> dict:
    active_periods = Period.active.all()

    for period in active_periods:
        trigger_date = period.date_end - timedelta(days=DAYS_BEFORE)
        if date.today() >= trigger_date and not period.reminder_mail_sent:
            send_internship_period_encoding_reminder(period)

    return {}
