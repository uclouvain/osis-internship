##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2019 Université catholique de Louvain
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
from django.utils.translation import gettext_lazy as _
from openpyxl import Workbook
from openpyxl.styles import Font

from internship import models
from internship.models.enums import organization_report_fields
from internship.models.internship_student_information import InternshipStudentInformation
from internship.utils.exporting.spreadsheet import columns_resizing, add_row
from osis_common.document.xls_build import save_virtual_workbook


def export_hospital_xls(cohort, organization):
    workbook = Workbook()
    worksheet = workbook.active
    _add_header(worksheet, organization)
    _add_students(worksheet, cohort, organization)
    _resize_columns(worksheet, organization)
    return save_virtual_workbook(workbook)


def _add_header(worksheet, organization):
    report_sequence = organization.report_sequence()
    column_titles = []
    for item in report_sequence:
        column_titles.append(str(_(item)))

    add_row(worksheet, column_titles)
    cells = worksheet.iter_rows(min_row=1, max_row=1, min_col=1, max_col=14)
    for col in cells:
        for cell in col:
            cell.font = Font(bold=True)


def _add_students(worksheet, cohort, organization):
    if cohort.is_parent:
        students_stat = models.internship_student_affectation_stat.InternshipStudentAffectationStat.objects.filter(
            organization__cohort__in=cohort.subcohorts.all(), organization__reference=organization.reference
        ).select_related('student__person')
    else:
        students_stat = models.internship_student_affectation_stat.find_by_organization(
            cohort, organization
        ).select_related('student__person')

    rep_seq = list(organization.report_sequence())

    cohorts = cohort.subcohorts.all() if cohort.is_parent else [cohort]

    persons = students_stat.values('student__person')
    students_info_list = InternshipStudentInformation.objects.filter(person__in=persons, cohort__in=cohorts).distinct(
        'person'
    )
    students_info_dict = {stud_info.person_id: stud_info for stud_info in students_info_list}

    for student_stat in students_stat:
        student_info = students_info_dict[student_stat.student.person_id]
        address = student_info.person.personaddress_set.first()
        seq_dict = {organization_report_fields.PERIOD: student_stat.period.name,
                    organization_report_fields.START_DATE: student_stat.period.date_start.strftime("%d-%m-%Y"),
                    organization_report_fields.END_DATE: student_stat.period.date_end.strftime("%d-%m-%Y"),
                    organization_report_fields.LAST_NAME: student_info.person.last_name,
                    organization_report_fields.FIRST_NAME: student_info.person.first_name,
                    organization_report_fields.GENDER: student_info.person.gender,
                    organization_report_fields.SPECIALTY: student_stat.speciality.name,
                    organization_report_fields.BIRTHDATE: student_info.person.birth_date.strftime("%d-%m-%Y")
                    if student_info.person.birth_date else None,
                    organization_report_fields.EMAIL: student_info.person.email,
                    organization_report_fields.NOMA: student_stat.student.registration_id,
                    organization_report_fields.PHONE: student_info.phone_mobile,
                    organization_report_fields.ADDRESS: address.location,
                    organization_report_fields.POSTAL_CODE: address.postal_code,
                    organization_report_fields.CITY: address.city}

        columns = []
        for seq in rep_seq:
            columns.append(seq_dict[seq])

        add_row(worksheet, columns)


def _resize_columns(worksheet, organization):
    # Take all allowed fields and associate their spreadsheet sizes.
    report_fields = organization_report_fields.REPORT_FIELDS
    fields_size = dict(zip(report_fields, [8, 13, 11, 32, 16, 5, 32, 16, 36, 11, 11, 11, 11, 11]))

    # Take the sequence of fields selected by the user and generate a list of their sizes
    selected_fields = list(organization.report_sequence())
    sizes_selected_fields = [fields_size[field] for field in selected_fields]

    # Associate columns' letters with their sizes, as required by the function columns_resizing.
    columns_size = dict(zip(_char_range('A', 'N'), sizes_selected_fields))
    columns_resizing(worksheet, columns_size)


def _char_range(a, z):
    for c in range(ord(a), ord(z) + 1):
        yield chr(c)
