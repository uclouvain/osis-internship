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

from base.models.student import Student
from internship.models.internship import Internship
from osis_common.models.serializable_model import SerializableModel, SerializableModelAdmin


class InternshipChoiceAdmin(SerializableModelAdmin):
    list_display = ('student', 'organization', 'speciality', 'choice', 'internship', 'priority', 'registered')
    fieldsets = ((None, {'fields': ('student', 'organization', 'speciality', 'choice', 'internship', 'priority')}),)
    raw_id_fields = ('student', 'organization', 'speciality')
    list_filter = ('speciality', 'choice', 'internship', 'organization')
    search_fields = ['student__person__first_name', 'student__person__last_name']


class InternshipChoice(SerializableModel):
    student = models.ForeignKey('base.Student', on_delete=models.CASCADE)
    organization = models.ForeignKey('internship.Organization', on_delete=models.CASCADE)
    speciality = models.ForeignKey('internship.InternshipSpeciality', null=True, on_delete=models.CASCADE)
    choice = models.IntegerField()
    internship = models.ForeignKey('internship.Internship', on_delete=models.CASCADE)
    priority = models.BooleanField()
    registered = models.DateTimeField(null=True)

    def __str__(self):
        return u"%s - %s : %s" % (self.organization.acronym, self.speciality.acronym, self.choice)

    class Meta:
        unique_together = (("student", "internship", "choice"),)


def search(**kwargs):
    kwargs = {k: v for k, v in kwargs.items() if v}
    return InternshipChoice.objects.filter(**kwargs)\
                                   .select_related("student", "organization", "speciality")\
                                   .order_by('choice')


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


def get_number_first_choice_by_organization(speciality, internship_id):
    internship = Internship.objects.get(pk=internship_id)
    return InternshipChoice.objects.filter(
        choice=1,
        speciality=speciality,
        internship__speciality_id=internship.speciality_id,
        internship_id=internship_id
    ).values("organization").annotate(models.Count("organization"))


def find_priority_choices(internship):
    try:
        return InternshipChoice.objects.filter(internship__in=internship, priority=True)
    except TypeError:
        return InternshipChoice.objects.filter(internship=internship, priority=True)


def find_regular_choices(internship):
    try:
        return InternshipChoice.objects.filter(internship__in=internship, priority=False)
    except TypeError:
        return InternshipChoice.objects.filter(internship=internship, priority=False)


def find_students_with_priority_choices(internship):
    return Student.objects.filter(id__in=find_priority_choices(internship).values("student").distinct()).select_related(
        'person'
    )


def find_students_with_regular_choices(internship):
    return Student.objects.filter(id__in=find_regular_choices(internship).values("student").distinct()).select_related(
        'person'
    )
