from celery.schedules import crontab

from backoffice.celery import app as celery_app
from . import send_period_encoding_reminder_mail

celery_app.conf.beat_schedule.update({
    '|Internship| Send period encoding reminder': {
        'task': 'internship.tasks.send_period_encoding_reminder_mail.run',
        # execute daily at 8am
        'schedule': crontab(minute=0, hour=8)
    },
})
