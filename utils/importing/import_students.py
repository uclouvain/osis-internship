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
from copy import copy

from openpyxl import load_workbook

from base.models import student
from internship.models import internship_student_information as mdl_isi


def import_xlsx(cohort, xlsxfile):
    diff = []
    workbook = load_workbook(filename=xlsxfile, read_only=True)
    worksheet = workbook.active
    for row in list(worksheet.rows)[1:]:
        _import_row(cohort, row, diff)
    xlsxfile.close()
    return diff


def _import_row(cohort, row, diff):
    matricule = row[7].value
    existing_student = student.find_by_registration_id(matricule)
    if existing_student:
        internship_student_information = mdl_isi.find_by_person(existing_student.person, cohort).first()
        if internship_student_information:
            student_information_diff = _update_information(internship_student_information, cohort, row)
            if(student_information_diff):
                diff.append(student_information_diff)
        else:
            student_information = mdl_isi.InternshipStudentInformation()
            student_information.person = existing_student.person
            _update_information(student_information, cohort, row)
            diff.append({
                "data": student_information,
                "new_record": True,
            })


def _update_information(information, cohort, row):
    old_data = copy(information)
    information.location = row[15].value
    information.postal_code = str(row[16].value)
    information.city = row[17].value
    information.country = row[18].value
    information.email = row[19].value
    information.phone_mobile = str(row[14].value)
    information.cohort = cohort
    return _get_data_differences(old_data, information)


def _get_data_differences(old, new):
    if old._cohort_cache:
        old._cohort_cache = new._cohort_cache
    new_set = set(new.__dict__.items()) - set(old.__dict__.items())
    data_diff = {
        "data": new,
        "diff_set": new_set,
        "original_data": old.__dict__,
        "new_record": False
    } if new_set else None
    return data_diff
