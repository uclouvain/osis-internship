##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2022 Université catholique de Louvain
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
from django.db.models import Window, F
from django.db.models.functions import RowNumber
from django.template.loader import render_to_string
from weasyprint import HTML

from internship.models.internship_score import InternshipScore
from internship.models.internship_student_affectation_stat import InternshipStudentAffectationStat
from osis_common.utils.url_fetcher import django_url_fetcher


def generate_pdf(cohort, periods, student, internships, mapping, extra_data):  # pylint: disable=too-many-arguments
    internships_scores = InternshipScore.objects.filter(
        student_affectation__student__person=student.person, validated=True
    ).filter(
        student_affectation__period__in=periods,
    ).select_related(
        'student_affectation__student__person', 'student_affectation__period__cohort'
    ).annotate(
        period_aff_index=Window(
            expression=RowNumber(),
            partition_by=[F('student_affectation__student'), F('student_affectation__period')],
            order_by=F('student_affectation__id').asc(),
        )
    ).order_by('student_affectation__period', 'period_aff_index')

    students_affectations = InternshipStudentAffectationStat.objects.filter(
        student__person=student.person,
        period__cohort=cohort,
    ).select_related(
        'student', 'period', 'speciality'
    ).values(
        'student__person', 'student__registration_id', 'period__name', 'organization__reference', 'organization__name',
        'speciality__acronym', 'speciality__sequence', 'speciality__name', 'internship__speciality_id',
        'internship__name', 'internship__length_in_periods', 'internship_evaluated'
    ).order_by('period__date_start')

    html_string = render_to_string('internship_summary_template.html', {**locals()})
    html = HTML(string=html_string, url_fetcher=django_url_fetcher, base_url="file:")
    return html.write_pdf(presentational_hints=True)
