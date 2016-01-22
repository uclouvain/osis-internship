
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
from django import template

register = template.Library()

COLOR_1 = ""
COLOR_2 = ""
COLOR_CURRENT = ""

@register.filter
def previous(value, arg):
    arg = arg-1

    if arg > 0:
        try:
            previous_e = value[int(arg)-1]
            current_e = value[int(arg)]
            global COLOR_1, COLOR_2, COLOR_CURRENT
            if previous_e.learning_unit_enrollment.offer_enrollment.offer_year.acronym != current_e.learning_unit_enrollment.offer_enrollment.offer_year.acronym:
                if COLOR_CURRENT == COLOR_1:
                    COLOR_CURRENT = COLOR_2
                else:
                    COLOR_CURRENT = COLOR_1
                # pass
            return COLOR_CURRENT
            # return value[int(arg)-1]
        except:
            return COLOR_CURRENT
    else:
        global COLOR_1, COLOR_2, COLOR_CURRENT
        COLOR_1 = "#FFFFFF"
        COLOR_2 = "#e5f2ff"
        COLOR_CURRENT=COLOR_1
        COLOR_CURRENT = COLOR_1
        return COLOR_CURRENT
