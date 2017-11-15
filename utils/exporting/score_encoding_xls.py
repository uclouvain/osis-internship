##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2017 Université catholique de Louvain
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
from openpyxl import Workbook
from openpyxl.writer.excel import save_virtual_workbook
from openpyxl.styles import colors, Font
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from internship import models
from internship.utils.exporting.spreadsheet import columns_resizing


def export_xls(cohort):
    workbook = Workbook()
    worksheet = workbook.active
    _add_header(cohort, worksheet)
    _add_students(cohort, worksheet)
    columns_resizing(worksheet, {'A': 45, 'B': 11, 'C': 8, 'D': 8, 'E': 8, 'F': 8, 'G': 8, 'H': 8, 'I': 8, 'J': 8,
                                 'K': 8, 'L': 8, 'M': 8, 'N': 8})
    return save_virtual_workbook(workbook)


def _add_header(cohort, worksheet):
    _add_row(worksheet, [str(cohort.name)])
    cell_title = worksheet["A1"]
    cell_title.font = Font(size=18, bold=True)
    worksheet.row_dimensions[1].height = 30
    _add_row(worksheet)
    date_format = str(_('date_format'))
    printing_date = timezone.now()
    printing_date = printing_date.strftime(date_format)
    _add_row(worksheet, [str('%s: %s' % (_('file_production_date'), printing_date))])
    _add_row(worksheet)

    periods = models.period.find_by_cohort(cohort)
    column_titles = ["Étudiant", "NOMA"]
    for period in periods:
        column_titles.append(period.name)
    _add_row(worksheet, column_titles)
    cells = worksheet.range("A5:N5")[0]
    for cell in cells:
        cell.font = Font(bold=True)


def _add_students(cohort, worksheet):
    students_stat = models.internship_student_affectation_stat.find_by_cohort(cohort)
    previous_student = None
    columns = []
    for student_stat in students_stat:
        if student_stat.student.registration_id != previous_student:
            if len(columns) > 0:
                _add_row(worksheet, columns)
                columns = []
            columns.append("{}, {}".format(student_stat.student.person.last_name.upper(),
                                           student_stat.student.person.first_name))
            columns.append(student_stat.student.registration_id)
            _add_period(columns, student_stat)
            previous_student = student_stat.student.registration_id
        else:
            _add_period(columns, student_stat)


def _add_period(columns, student_stat):
    period_number = student_stat.period.number() + 1 # Increment to ignore the two first columns
    if len(columns) < period_number:
        diff = period_number - len(columns)
        while diff > 0:
            columns.append("")
            diff -= 1
    columns.append("{}{}".format(student_stat.speciality.acronym, student_stat.organization.reference))


def _add_row(worksheet, content=None):
    if content:
        worksheet.append(content)
    else:
        worksheet.append([str('')])
