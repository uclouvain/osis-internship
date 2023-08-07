from backoffice.celery import app as celery_app
from base.utils.date import working_days_count
from internship.models.period import Period
from internship.utils.mails.mails_management import send_internship_score_encoding_recaps


@celery_app.task
def run() -> dict:
    active_period = Period.active.first()
    working_days_left = working_days_count(active_period.date_end)
    if working_days_left == 1:
        send_internship_score_encoding_recaps(active_period)
    return {}
