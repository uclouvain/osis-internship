##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django.db import models
from osis_common.models.serializable_model import SerializableModel, SerializableModelAdmin
from internship.models.enums.affectation_type import AffectationType
from internship.models.enums.choice_type import ChoiceType
from internship.models.enums.costs import Costs


class InternshipStudentAffectationStatAdmin(SerializableModelAdmin):
    list_display = ('student', 'organization', 'speciality', 'period', 'internship', 'choice', 'cost',
                    'consecutive_month', 'type', 'internship_evaluated')
    fieldsets = ((None, {'fields': ('student', 'organization', 'speciality', 'period', 'internship', 'choice', 'cost',
                                    'consecutive_month', 'type','internship_evaluated')}),)
    raw_id_fields = ('student', 'organization', 'speciality', 'period', 'internship')
    search_fields = ['student__person__first_name', 'student__person__last_name']
    list_filter = ('period__cohort', 'choice')


class InternshipStudentAffectationStat(SerializableModel):
    student = models.ForeignKey('base.Student', on_delete=models.CASCADE)
    organization = models.ForeignKey('internship.Organization', on_delete=models.CASCADE)
    speciality = models.ForeignKey('internship.InternshipSpeciality', on_delete=models.CASCADE)
    period = models.ForeignKey('internship.Period', on_delete=models.CASCADE)
    internship = models.ForeignKey(
        'internship.Internship', blank=True, null=True,
        on_delete=models.CASCADE
    )
    choice = models.CharField(max_length=1, choices=ChoiceType.choices(), default=ChoiceType.NO_CHOICE.value)
    cost = models.IntegerField()
    consecutive_month = models.BooleanField(default=False)
    type = models.CharField(max_length=1, choices=AffectationType.choices(), default=AffectationType.NORMAL.value)
    internship_evaluated = models.BooleanField(default=False)

    def __str__(self):
        return u"%s : %s - %s (%s)" % (self.student, self.organization, self.speciality, self.period)


def search(**kwargs):
    kwargs = {k: v for k, v in kwargs.items() if v}
    return InternshipStudentAffectationStat.objects.filter(**kwargs) \
        .select_related("student__person", "organization", "speciality", "period") \
        .order_by("student__person__last_name", "student__person__first_name", "period__date_start")


def find_non_mandatory_affectations(period_ids):
    return InternshipStudentAffectationStat.objects.filter(period__id__in=period_ids). \
        select_related("student", "organization", "speciality")


def find_by_cohort(cohort):
    return InternshipStudentAffectationStat.objects.filter(period__cohort=cohort). \
        order_by("student__person__last_name",
                 "student__person__first_name",
                 "period__date_start")


def find_by_organization(cohort, organization):
    return InternshipStudentAffectationStat.objects.filter(period__cohort=cohort, organization=organization). \
        order_by("period__date_start",
                 "student__person__last_name",
                 "student__person__first_name")


def find_by_student(student, cohort):
    return InternshipStudentAffectationStat.objects.filter(student=student, period__cohort=cohort)


def delete_affectations(student, cohort):
    affectations = find_by_student(student, cohort)
    affectations.delete()


def build(student, organization, specialty, period, internship, student_choices):
    affectation = InternshipStudentAffectationStat()
    affectation.student = student
    affectation.organization = organization
    affectation.period = period
    affectation.internship = internship

    if internship is None or internship.speciality is None:
        affectation.speciality = specialty
    else:
        affectation.speciality = internship.speciality

    check_choice = False
    for student_choice in student_choices:
        if student_choice.organization == organization:
            affectation.choice = student_choice.choice
            check_choice = True
            if student_choice.choice == 1:
                affectation.cost = Costs.FIRST_CHOICE.value
            elif student_choice.choice == 2:
                affectation.cost = Costs.SECOND_CHOICE.value
            elif student_choice.choice == 3:
                affectation.cost = Costs.THIRD_CHOICE.value
            elif student_choice.choice == 4:
                affectation.cost = Costs.FORTH_CHOICE.value
    if not check_choice:
        affectation.choice = ChoiceType.IMPOSED.value
        affectation.cost = Costs.IMPOSED.value

    return affectation
