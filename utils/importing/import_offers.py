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
import logging

import openpyxl
from django.conf import settings

from internship.models import organization, internship_speciality, internship_offer, period, period_internship_places
from internship.models.period_internship_places import PeriodInternshipPlaces

COL_REF_HOSPITAL = 0
COL_SPECIALTY = 1
COL_MASTER = 2

logger = logging.getLogger(settings.DEFAULT_LOGGER)


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
        hospitals = organization.find_by_reference(cohort, row[COL_REF_HOSPITAL].value)
        if hospitals:
            _import_hospital_places(row, cohort, hospitals)


def _import_hospital_places(row, cohort, hospitals):
    periods = period.Period.objects.filter(cohort=cohort)
    maximum_enrollments = _get_maximum_enrollments(row, periods)

    logger.info("Importing places of the hospital {}".format(hospitals.first()))
    specialities = internship_speciality.search(acronym__exact=row[COL_SPECIALTY].value, cohort=cohort)
    for specialty in specialities:
        logger.info("Importing places of the speciality {}".format(specialty))
        offer = _create_offer(row, cohort, specialty, hospitals.first(), maximum_enrollments)

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
        logger_message = "Updating offer {}"
        offer = existing_internship_offer.first()
    else:
        logger_message = "Creating offer {}"
        offer = internship_offer.InternshipOffer()
    logger.info(logger_message.format(offer))

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
    existing_places = PeriodInternshipPlaces.objects.filter(
        period=a_period,
        internship_offer=offer
    )

    if existing_places:
        logger_message = "Updating places {}"
        offer_places = existing_places.first()
    else:
        logger_message = "Creating places {}"
        offer_places = period_internship_places.PeriodInternshipPlaces()

    offer_places.period = a_period
    offer_places.internship_offer = offer
    if value:
        offer_places.number_places = int(value)
    else:
        offer_places.number_places = 0
    offer_places.save()
    logger.info(logger_message.format(offer_places))


def _is_invalid_id(registration_id):
    if registration_id is None or registration_id == 0:
        return True
    else:
        try:
            int(registration_id)
            return False
        except ValueError:
            return True
