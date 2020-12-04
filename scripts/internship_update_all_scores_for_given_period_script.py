'''
Python script to update all student internship scores for period P7 in cohort R6-2020 with excused field set to True and
score set to 17 due to usual evaluation workflow not applicable in the context of COVID-19 crisis.
'''
from internship.models.internship_score import InternshipScore
from internship.models.period import Period


def run():
    period = Period.objects.get(name='P7', cohort__name="R6-2020")
    InternshipScore.objects.filter(period=period, cohort=period.cohort, excused=True).update(score=17)
