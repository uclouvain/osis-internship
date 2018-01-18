##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2017 Université catholique de Louvain (http://www.uclouvain.be)
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
from openpyxl import load_workbook
from base.models import student
from internship.models import internship_student_information as mdl_isi


def import_xlsx(cohort, xlsxfile):
    workbook = load_workbook(filename=xlsxfile, read_only=True)
    worksheet = workbook.active
    mdl_isi.remove_all(cohort)
    for row in list(worksheet.rows)[1:]:
        _import_row(cohort, row)

    xlsxfile.close()


def _import_row(cohort, row):
    matricule = row[7].value
    existing_student = student.find_by_registration_id(matricule)
    if existing_student:
        student_information = mdl_isi.InternshipStudentInformation()
        student_information.person = existing_student.person
        student_information.location = row[15].value
        student_information.postal_code = row[16].value
        student_information.city = row[17].value
        student_information.country = row[18].value
        student_information.email = row[19].value
        student_information.phone_mobile = row[14].value
        student_information.cohort = cohort
        student_information.save()
