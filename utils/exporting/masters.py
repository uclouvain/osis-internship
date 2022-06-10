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

from django.db.models import Q
from django.utils.translation import gettext as _
from openpyxl import Workbook
from openpyxl.styles import Font
from openpyxl.writer.excel import save_virtual_workbook

from base.models.person import Person
from base.models.person_address import PersonAddress
from internship.models.internship_master import InternshipMaster
from internship.models.master_allocation import MasterAllocation
from internship.utils.exporting.spreadsheet import add_row

LAST_COLUMN = 50
PERIOD_COLUMN_WIDTH = 7
MAX_COL_LENGTH = 25
FIELDS = [
    'last_name', 'first_name', 'civility', 'gender', 'email', 'email_private', 'email_additional',
    'location', 'postal_code', 'city', 'country', 'phone', 'phone_mobile', 'birth_date', 'start_activities', 'role'
]


def export_xls(cohort_id):
    workbook = Workbook()
    worksheet = workbook.active
    models_fields = set(InternshipMaster._meta.fields)
    models_fields |= set(Person._meta.fields)
    models_fields |= set(PersonAddress._meta.fields)
    meta_fields = [field for field in models_fields if field.name in FIELDS]
    sorted_fields = sorted(meta_fields, key=lambda x: FIELDS.index(x.name))
    _add_header(worksheet, sorted_fields)
    _add_masters(worksheet, sorted_fields, cohort_id)
    _adjust_column_width(worksheet)
    return save_virtual_workbook(workbook)


def _add_header(worksheet, fields):
    fields_verbose_names = [_(field.verbose_name.capitalize()) for field in fields]
    fields_verbose_names.extend([_("Specialty"), _("Organization"), "Ref", "Role"])
    add_row(worksheet, fields_verbose_names)
    worksheet.row_dimensions[1].font = Font(bold=True)


def _add_masters(worksheet, fields, cohort_id):
    fields_names = _build_fields_names(fields)
    masters = MasterAllocation.objects.filter(
        Q(specialty__cohort_id=cohort_id) | Q(organization__cohort_id=cohort_id)
    ).values_list(
        *fields_names, 'specialty__name', 'organization__name', 'organization__reference', 'role'
    ).distinct()
    for master in masters:
        add_row(worksheet, master)


def _build_fields_names(fields):
    fields_names = []
    for field in fields:
        if field in InternshipMaster._meta.fields:
            fields_names.append('master__{}'.format(field.name))
        elif field in Person._meta.fields:
            fields_names.append('master__person__{}'.format(field.name))
        elif field in PersonAddress._meta.fields:
            fields_names.append('master__person__personaddress__{}'.format(field.name))
        else:
            fields_names.append(field.name)
    return fields_names


def _adjust_column_width(worksheet):
    for column_cells in worksheet.columns:
        length = max(len(str(cell.value)) for cell in column_cells)
        length = length if length <= MAX_COL_LENGTH else MAX_COL_LENGTH
        worksheet.column_dimensions[column_cells[0].column].width = length
