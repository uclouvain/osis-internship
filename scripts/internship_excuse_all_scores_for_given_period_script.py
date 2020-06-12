'''
Python script to create all student internship scores for period P7 in cohort R6-2020 with excused field set to True and
score set to 17 due to usual evaluation workflow not applicable in the context of COVID-19 crisis.
'''
from internship.models.internship_score import InternshipScore
from internship.models.internship_student_affectation_stat import InternshipStudentAffectationStat
from internship.models.period import Period


def run():
    period = Period.objects.get(name='P7', cohort__name="R6-2020")

    affectations = InternshipStudentAffectationStat.objects.filter(
        period=period, organization__isnull=False
    ).distinct('student')

    scores_to_create = []
    for affectation in affectations:
        scores_to_create.append(
            InternshipScore(**{
                'student_id': affectation.student.id,
                'period_id': period.id,
                'cohort_id': period.cohort.id,
                'excused': True
            })
        )

    scores = InternshipScore.objects.bulk_create(scores_to_create)
