##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2016 Université catholique de Louvain (http://www.uclouvain.be)
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
from internship.models import internship


class InternshipChoiceAdmin(SerializableModelAdmin):
    list_display = ('student', 'organization', 'speciality', 'choice', 'internship', 'priority')
    fieldsets = ((None, {'fields': ('student', 'organization', 'speciality', 'choice', 'internship',
                                    'priority')}),)
    raw_id_fields = ('student', 'organization', 'speciality')
    list_filter = ('speciality', 'choice', 'internship')
    search_fields = ['student__person__first_name', 'student__person__last_name']


class InternshipChoice(SerializableModel):
    student = models.ForeignKey('base.Student')
    organization = models.ForeignKey('internship.Organization')
    speciality = models.ForeignKey('internship.InternshipSpeciality', null=True)
    choice = models.IntegerField()
    internship = models.ForeignKey('internship.Internship')
    priority = models.BooleanField()

    def __str__(self):
        return u"%s - %s : %s" % (self.organization.acronym, self.speciality.acronym, self.choice)


def find_by_all_student():
    return InternshipChoice.objects.all().distinct('student').select_related("student", "organization", "speciality")


def find_by_student(s_student):
    return InternshipChoice.objects.filter(student=s_student)\
                                   .select_related("student", "organization", "speciality")\
                                   .order_by('choice')


def find_by_student_desc(s_student):
    return InternshipChoice.objects.filter(student=s_student)\
                                   .select_related("student", "organization", "speciality")\
                                   .order_by('-choice')


def search(**kwargs):
    kwargs = {k: v for k, v in kwargs.items() if v}
    return InternshipChoice.objects.filter(**kwargs)\
                                   .select_related("student", "organization", "speciality")\
                                   .order_by('choice')


def search_other_choices(**kwargs):
    kwargs = {k: v for k, v in kwargs.items() if v}
    queryset = InternshipChoice.objects.filter(**kwargs)\
                                       .select_related("student", "organization", "speciality")\
                                       .order_by('choice')
    return queryset.exclude(choice=1)


def search_by_student_or_choice(student=None, internship=None):
    has_criteria = False
    queryset = InternshipChoice.objects

    if student:
        queryset = queryset.filter(student=student)
        has_criteria = True

    if internship is not None:
        queryset = queryset.filter(internship=internship)
        has_criteria = True

    if has_criteria:
        return queryset.order_by("choice")
    else:
        return None


def get_non_mandatory_internship_choices(cohort):
    internships = internship.Internship.objects.filter(cohort=cohort, speciality=None)
    return InternshipChoice.objects.filter(internship_id__in=internships.values_list("id", flat=True)).\
        select_related("student", "organization", "speciality", "internship")


def get_internship_choices_made(cohort, student):
    internships = internship.Internship.objects.filter(cohort=cohort, speciality=None)
    return InternshipChoice.objects.filter(internship_id__in=internships.values_list("id", flat=True), student=student).\
        values_list("internship_id", flat=True).distinct()


def get_number_students(cohort):
    return InternshipChoice.objects.filter(internship__cohort=cohort).distinct("student").count()


def get_number_first_choice_by_organization(speciality):
    return InternshipChoice.objects.filter(choice=1, speciality=speciality).values("organization")\
        .annotate(models.Count("organization"))
