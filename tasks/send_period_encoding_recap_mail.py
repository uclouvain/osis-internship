import datetime

import numpy as np

from backoffice.celery import app as celery_app
from internship.models.period import Period
from internship.utils.mails.mails_management import send_internship_period_encoding_recap


@celery_app.task
def run() -> dict:
    active_period = Period.active.first()
    working_days_left = np.busday_count(datetime.date.today(), active_period.date_end)
    if working_days_left == 1:
        send_internship_period_encoding_recap(active_period)
    return {}
