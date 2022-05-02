##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2022 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.template.defaulttags import register

from internship.models.internship_speciality import InternshipSpeciality
from internship.models.internship_student_affectation_stat import InternshipStudentAffectationStat
from internship.models.organization import Organization


@register.filter()
def has_remedial(student, period=None):
    qs = InternshipStudentAffectationStat.objects.filter(student__person=student.person, period__remedial=True)
    if period:
        qs = qs.filter(period=period)
    return qs.exists()


@register.filter()
def is_searched_reference(reference, request) -> bool:

    organization = None
    specialty = None

    if request.GET.get('organization'):
        organization = Organization.objects.get(pk=request.GET.get('organization'))

    if request.GET.get('specialty'):
        specialty = InternshipSpeciality.objects.get(pk=request.GET.get('specialty'))

    searched_organization = organization.reference in reference if organization else False
    searched_specialty = specialty.acronym in reference if specialty else False

    if request.GET.get('organization') and request.GET.get('specialty'):
        return searched_organization and searched_specialty
    else:
        return searched_organization or searched_specialty

