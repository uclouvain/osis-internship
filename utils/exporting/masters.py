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
from django.db.models import OuterRef, Subquery
from django.utils.translation import gettext as _
from openpyxl import Workbook
from openpyxl.styles import Font
from openpyxl.writer.excel import save_virtual_workbook

from internship.models.internship_master import InternshipMaster, InternshipMasterAdmin
from internship.models.master_allocation import MasterAllocation
from internship.utils.exporting.spreadsheet import add_row

LAST_COLUMN = 50
PERIOD_COLUMN_WIDTH = 7
MAX_COL_LENGTH = 25
FIELDS = [
    'last_name', 'first_name', 'civility', 'gender', 'email', 'email_private', 'location', 'postal_code', 'city',
    'country', 'phone', 'phone_mobile', 'birth_date', 'start_activities'
]


def export_xls():
    workbook = Workbook()
    worksheet = workbook.active
    fields = _custom_sort_fields([
        {'name': f.name, 'verbose_name': _(f.verbose_name.capitalize())}
        for f in InternshipMaster._meta.fields if f.name in FIELDS
    ])
    _add_header(worksheet, fields)
    _add_masters(worksheet, fields)
    _adjust_column_width(worksheet)
    return save_virtual_workbook(workbook)


def _add_header(worksheet, fields):
    fields_verbose_names = [field['verbose_name'] for field in fields]
    fields_verbose_names.extend([_("Specialty"), _("Organization")])
    add_row(worksheet, fields_verbose_names)
    worksheet.row_dimensions[1].font = Font(bold=True)


def _add_masters(worksheet, fields):
    master_allocation = MasterAllocation.objects.filter(master=OuterRef('pk'))
    masters = InternshipMaster.objects.all().order_by('last_name', 'first_name').annotate(
        specialty=Subquery(master_allocation.values('specialty__name')[:1]),
        organization=Subquery(master_allocation.values('organization__name')[:1])
    ).values(*FIELDS, 'specialty', 'organization').distinct()
    for master in masters:
        add_row(worksheet, list(master.values()))


def _adjust_column_width(worksheet):
    for column_cells in worksheet.columns:
        length = max(len(str(cell.value)) for cell in column_cells)
        length = length if length <= MAX_COL_LENGTH else MAX_COL_LENGTH
        worksheet.column_dimensions[column_cells[0].column].width = length


def _custom_sort_fields(fields):
    ordered_field_names = InternshipMasterAdmin.fieldsets[0][1]['fields']
    ordered_fields = sorted(fields, key=lambda x: ordered_field_names.index(x['name']))
    return ordered_fields
