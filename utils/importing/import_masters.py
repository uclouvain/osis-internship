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
from internship.models.internship_master import InternshipMaster
from internship.models.master_allocation import MasterAllocation
from internship.models.enums.civility import Civility
from internship.models.enums.mastery import Mastery
from internship.models.enums.gender import Gender
from internship.models import internship_speciality
from internship.models import organization
from internship.models import cohort as mdl_cohort


# This module is temporary. Once the internship masters are successfully
# imported in the database, it must be removed.


def import_xls():
    wb = load_workbook(filename='internship/utils/resources/masters.xlsx', read_only=True)
    ws = wb.active
    InternshipMaster.objects.all().delete()
    MasterAllocation.objects.all().delete()

    cohorts = mdl_cohort.find_all()

    for coh in cohorts:
        for row in list(ws.rows)[1:]:
            master, allocation = import_masters(coh, row)
            master.save()
            allocation.master = master
            allocation.save()
        print(coh)


def import_masters(cohort, row):
    master = InternshipMaster()
    allocation = MasterAllocation()
    for cell in row:
        if cell.value:  # ignores column titles and empty cells.
            _import_civility(master, cell)
            _import_mastery(master, cell)
            _import_gender(master, cell)
            _import_name(master, cell)
            _import_allocation(allocation, cell, cohort)
            _import_emails(master, cell)
            _import_start_activities(master, cell)
            _import_address(master, cell)
            _import_phones(master, cell)
            _import_birth_date(master, cell)

    return master, allocation


def _import_civility(master, cell):
    if cell.column == 1:
        master.civility = Civility.PROFESSOR.value if cell.value == "Pr" else Civility.DOCTOR.value


def _import_mastery(master, cell):
    if cell.column == 2:
        if cell.value == "spécialiste":
            master.type_mastery = Mastery.SPECIALIST.value
        else:
            master.type_mastery = Mastery.GENERALIST.value


def _import_gender(master, cell):
    if cell.column == 3:
        if cell.value == "F":
            master.gender = Gender.FEMALE.value
        else:
            master.gender = Gender.MALE.value


def _import_name(master, cell):
    if cell.column == 4:
        master.first_name = cell.value.strip()
    elif cell.column == 5:
        master.last_name = cell.value.strip()


def _import_allocation(allocation, cell, cohort):
    if cell.column == 6:
        specialty_acronym = cell.value
        specialties = internship_speciality.find_by_acronym(cohort, specialty_acronym)
        if specialties:
            allocation.specialty = specialties[0]
    elif cell.column == 8:
        hospital_reference = cell.value
        hospitals = organization.find_by_reference(cohort, hospital_reference)
        if hospitals:
            allocation.organization = hospitals[0]


def _import_emails(master, cell):
    if cell.column == 10:
        master.email = cell.value
    elif cell.column == 18:
        master.email_private = cell.value


def _import_start_activities(master, cell):
    if cell.column == 11:
        master.start_activities = cell.value


def _import_address(master, cell):
    if cell.column == 12:
        master.location = cell.value
    elif cell.column == 14:
        master.postal_code = cell.value
    elif cell.column == 16:
        master.city = cell.value


def _import_phones(master, cell):
    if cell.column == 20 or cell.column == 21:
        if not master.phone:
            master.phone = cell.value
    elif cell.column == 22:
        master.phone_mobile = cell.value


def _import_birth_date(master, cell):
    if cell.column == 23:
        master.birth_date = cell.value
