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
from openpyxl.styles import Font
from internship import models
from internship.utils.exporting.spreadsheet import columns_resizing, add_row


def export_xls(cohort):
    workbook = Workbook()
    worksheet = workbook.active
    _add_header(cohort, worksheet)
    _add_students(cohort, worksheet)
    columns_resizing(worksheet, {'A': 32, 'B': 16, 'C': 11, 'D': 5, 'E': 7, 'F': 5, 'G': 7, 'H': 5, 'I': 7, 'J': 5,
                                 'K':  7, 'L':  5, 'M':  7, 'N': 5, 'O': 7, 'P': 5, 'Q': 7, 'R': 5, 'S': 7, 'T': 5,
                                 'U':  7, 'V':  5, 'W':  7, 'X': 5, 'Y': 7, 'Z': 5, 'AA': 7})
    return save_virtual_workbook(workbook)


def _add_header(cohort, worksheet):
    periods = models.period.find_by_cohort(cohort)
    column_titles = ["Nom", "Prénom", "NOMA"]
    for period in periods:
        column_titles.append(period.name)
        column_titles.append("{}+".format(period.name))
    add_row(worksheet, column_titles)
    cells = worksheet.range("A1:AA1")[0]
    for cell in cells:
        cell.font = Font(bold=True)


def _add_students(cohort, worksheet):
    students_stat = models.internship_student_affectation_stat.find_by_cohort(cohort)
    previous_student = None
    columns = []
    for student_stat in students_stat:
        # Line breaking condition.
        if student_stat.student.registration_id != previous_student:
            if len(columns) > 0:
                add_row(worksheet, columns)
                columns = []
            columns.append(student_stat.student.person.last_name.upper())
            columns.append(student_stat.student.person.first_name)
            columns.append(student_stat.student.registration_id)
            _add_period(columns, student_stat)
            previous_student = student_stat.student.registration_id
        else:
            _add_period(columns, student_stat)


def _add_period(columns, student_stat):
    _deal_with_empty_periods()
    columns.append(student_stat.speciality.acronym)
    columns.append("{}{}".format(student_stat.speciality.acronym, student_stat.organization.reference))


def _deal_with_empty_periods(columns, student_stat):
    period_position = (student_stat.period.number() * 2) + 1  # Consider the first columns and 2 columns per period.
    if len(columns) < period_position:
        diff = period_position - len(columns)
        while diff > 0:  # Add empty columns when there is no data to the periods before the current one.
            columns.append("")
            columns.append("")
            diff -= 2  # Subtracts the number of columns appended within the while loop.
