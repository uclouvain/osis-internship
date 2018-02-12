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

def group_periods_by_consecutives(periods, length=1):
    if length == 1:
        for period in periods:
            yield [period]
    else:
        for i in range(len(periods) - (length - 1)):
            if all(map(lambda period: int(periods[i].name[1:]) + 1 == int(periods[i + 1].name[1:]),
                       periods[i: i + length])):
                yield periods[i: i + length]


def map_period_ids(periods):
    return list(map(lambda period: period.id, periods))
