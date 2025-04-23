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
from collections import Counter

from django.template.defaulttags import register


@register.filter
def get_item_at_index(list, index):
    return list[index]


@register.simple_tag
def iter_score_periods(periods, score_periods, key):
    if key not in [p.name for p in periods]:
        return []
    matching = [sp[0] for sp in score_periods if sp[0] == key]
    return matching if matching else [key]


@register.simple_tag
def count_multiple_score_for_period(score_periods):
    counts = Counter([el[0] for el in score_periods])
    total = sum(count>1 for count in counts.values())
    return total


@register.filter
def get_period_score_tuple(tuples, period):
    matches = [t[1] for t in tuples if t[0] == period]
    if not matches:
        return None
    elif len(matches) == 1:
        return matches[0]
    else:
        return matches
