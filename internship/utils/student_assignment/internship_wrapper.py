##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2016 Université catholique de Louvain (http://www.uclouvain.be)
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


class InternshipWrapper:
    def __init__(self, internship):
        self.internship = internship
        self.periods_places = dict()
        self.periods_places_left = dict()

    def set_period_places(self, period_places):
        period_name = period_places.period.name
        self.periods_places[period_name] = period_places
        self.periods_places_left[period_name] = period_places.number_places

    def period_is_not_full(self, period_name):
        return self.periods_places_left.get(period_name, 0) > 0

    def get_free_periods(self):
        return [period_name for period_name in self.periods_places_left.keys() if self.period_is_not_full(period_name)]

    def is_not_full(self):
        return len(self.get_free_periods()) > 0

    def occupy(self, period_name):
        self.periods_places_left[period_name] -= 1
        return self.periods_places[period_name]

    def reinitialize(self):
        self.periods_places_left = dict()
        for period_name, period_places in self.periods_places.items():
            self.periods_places_left[period_name] = period_places.number_places


