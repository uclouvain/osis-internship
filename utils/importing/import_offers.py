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
import openpyxl

from internship.models import organization, internship_speciality, internship_offer, period, period_internship_places

COL_REF_HOSPITAL = 0
COL_SPECIALTY = 1
COL_MASTER = 2


def import_xlsx(file_name, cohort):
    """ This import can be performed multiple times for the same cohort and the logic must make sure it will not
        produce duplicated data. """
    workbook = openpyxl.load_workbook(file_name, read_only=True)
    worksheet = workbook.active

    for row in worksheet.rows:
        _import_offer(row, cohort)


def _import_offer(row, cohort):
    if _is_invalid_id(row[COL_REF_HOSPITAL].value):
        return

    if row[COL_SPECIALTY].value:
        organizations = organization.find_by_reference(cohort, row[COL_REF_HOSPITAL].value)

        if organizations:
            _import_places(row, cohort, organizations)


def _import_places(row, cohort, organizations):
    periods = period.Period.objects.filter(cohort=cohort)
    maximum_enrollments = _get_maximum_enrollments(row, periods)

    specialities = internship_speciality.search(acronym__exact=row[COL_SPECIALTY].value, cohort=cohort)
    for specialty in specialities:
        offer = _create_offer(row, cohort, specialty, organizations.first(), maximum_enrollments)

        number_period = 1
        for x in range(3, len(periods) + 3):
            period_name = "P{}".format(number_period)
            number_period += 1
            _create_offer_places(cohort, period_name, offer, row[x].value)


def _get_maximum_enrollments(row, periods):
    maximum_enrollments = 0
    for col_period in range(3, len(periods) + 3):
        if row[col_period].value:
            maximum_enrollments += int(row[col_period].value)
    return maximum_enrollments


def _create_offer(row, cohort, specialty, org, maximum_enrollments):
    existing_internship_offer = internship_offer.InternshipOffer.objects.filter(speciality=specialty,
                                                                                organization__reference=org.reference,
                                                                                cohort=cohort)
    if existing_internship_offer:
        offer = existing_internship_offer.first()
    else:
        offer = internship_offer.InternshipOffer()

    offer.organization = org
    offer.speciality = specialty
    offer.title = specialty.name
    offer.maximum_enrollments = maximum_enrollments
    offer.master = row[COL_MASTER].value
    offer.cohort = cohort
    offer.selectable = True
    offer.save()
    return offer


def _create_offer_places(cohort, period_name, offer, value):
    a_period = period.search(name__exact=period_name, cohort=cohort).first()
    existing_places = period_internship_places.find_by_offer_in_period(a_period, offer)

    if existing_places:
        offer_places = existing_places.first()
    else:
        offer_places = period_internship_places.PeriodInternshipPlaces()

    offer_places.period = a_period
    offer_places.internship_offer = offer
    if value:
        offer_places.number_places = int(value)
    else:
        offer_places.number_places = 0
    offer_places.save()


def _is_invalid_id(registration_id):
    if registration_id is None or registration_id == 0:
        return True
    else:
        try:
            int(registration_id)
            return False
        except ValueError:
            return True
