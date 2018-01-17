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


def import_xlsx(file_name, cohort):
    workbook = openpyxl.load_workbook(file_name, read_only=True)
    worksheet = workbook.active
    col_reference = 0
    col_spec = 1
    col_master = 2

    # Iterates over the lines of the spreadsheet.
    for count, row in enumerate(worksheet.rows):
        if row[col_reference].value is None \
                or row[col_reference].value == 0 \
                or not _is_registration_id(row[col_reference].value):
            continue

        if row[col_spec].value is not None:
            if row[col_reference].value:
                if int(row[col_reference].value) < 10:
                    reference = "0" + str(row[col_reference].value)
                else:
                    reference = str(row[col_reference].value)
                org = organization.search(reference=reference, cohort=cohort)

            if len(org) > 0:
                spec_value = row[col_spec].value
                spec_value = spec_value.replace(" ", "")
                spec_value = spec_value.replace("*", "")

                master_value = row[col_master].value

                speciality = internship_speciality.search(acronym__exact=spec_value, cohort=cohort)

                number_place = 0
                periods = period.Period.objects.filter(cohort=cohort)
                for x in range(3, len(periods) + 3):
                    if row[x].value is None:
                        number_place += 0
                    else:
                        number_place += int(row[x].value)

                for x in range(0, len(speciality)):
                    check_internship_offer = internship_offer.InternshipOffer.objects.filter(
                        speciality=speciality[x],
                        organization__reference=org[0].reference,
                        cohort=cohort)
                    if len(check_internship_offer) != 0:
                        offer = check_internship_offer.first()
                    else:
                        offer = internship_offer.InternshipOffer()

                    offer.organization = org[0]
                    offer.speciality = speciality[x]
                    offer.title = speciality[x].name
                    offer.maximum_enrollments = number_place
                    offer.master = master_value
                    offer.cohort = cohort
                    offer.selectable = True
                    offer.save()

                    number_period = 1
                    for x in range(3, len(periods) + 3):
                        period_search = "P" + str(number_period)
                        number_period += 1
                        a_period = period.search(name__exact=period_search, cohort=cohort).first()
                        check_relation = period_internship_places.find_by_offer_in_period(a_period, offer)

                        if len(check_relation) != 0:
                            relation = period_internship_places.find_by_id(check_relation.first().id)
                        else:
                            relation = period_internship_places.PeriodInternshipPlaces()

                        relation.period = a_period
                        relation.internship_offer = offer
                        if row[x].value is None:
                            relation.number_places = 0
                        else:
                            relation.number_places = int(row[x].value)
                        relation.save()


def _is_registration_id(registration_id):
    try:
        int(registration_id)
        return True
    except ValueError:
        return False
