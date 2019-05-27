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
from django.db import transaction
from openpyxl import load_workbook

from base.models import student
from internship.models.internship_score import InternshipScore
from internship.models.period import Period

APDS_COUNT = 15
LINE_INTERVAL = 2


@transaction.atomic
def import_xlsx(cohort, xlsxfile, period):
    workbook = load_workbook(filename=xlsxfile, read_only=True)
    worksheet = workbook.active
    period = Period.objects.get(name=period, cohort=cohort)
    for row in list(worksheet.rows)[5:worksheet.max_row]:
        try:
            _import_score(row, cohort, period)
        except Exception:
            return row
    xlsxfile.close()


def _import_score(row, cohort, period):
    scores = []
    registration_id = row[0].value
    if registration_id is None:
        return
    for i in range(1, APDS_COUNT*LINE_INTERVAL, LINE_INTERVAL):
        scores.append(row[i+LINE_INTERVAL+1].value)
    existing_student = student.find_by_registration_id(registration_id)
    if existing_student:
        internship_score, created = InternshipScore.objects.get_or_create(
            student=existing_student, period=period, cohort=cohort
        )
        for index, score in enumerate(scores):
            internship_score.__setattr__('APD_{}'.format(index+1), score)
        internship_score.save()
    else:
        raise Exception
