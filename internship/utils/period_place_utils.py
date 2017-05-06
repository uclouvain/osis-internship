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

def get_period_places_for_offer_ids(offer_ids, period_places):
    return list(filter(lambda period_place: period_place["internship_offer_id"] in offer_ids, period_places))

def get_period_places_for_period_ids(period_ids, period_places):
    return list(filter(lambda period_place: period_place["period_id"] in period_ids, period_places))

def get_period_place_for_offer_and_period(offer, period, period_places):
    return list(filter(lambda period_place: period_place["internship_offer_id"] == offer.id \
            and period_place["period_id"] == period.id, period_places))[0]

def get_period_ids_from_period_places(period_places):
    return list(map(lambda period_place: period_place["period_id"], period_places))

def sort_period_places(period_places):
    unordered_period_places = list(filter(lambda period_place: period_place["number_places"] > 0, period_places))
    return list(sorted(unordered_period_places, key=lambda period_place: period_place["number_places"], reverse=True))

def replace_period_place_in_dictionnary(period_place, period_places_dictionnary, new_count):
    for period_place_dict in period_places_dictionnary:
        if period_place_dict["id"] == period_place["id"]:
            period_place_dict["number_places"] = new_count
