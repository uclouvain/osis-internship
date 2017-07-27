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
from django import template
from django.utils.translation import ugettext_lazy as _

register = template.Library()


@register.filter
def academic_years(a_learning_container):
    if a_learning_container.start_year and a_learning_container.auto_renewal_until:
        start_yr = ''
        end_year = ''
        if a_learning_container.start_year:
            start_yr = "{} {}-{}".format(_('of').title(), a_learning_container.start_year, str(a_learning_container.start_year+1)[-2:])
        if a_learning_container.auto_renewal_until:
            end_year = "{} {}-{}".format(_('to'), a_learning_container.auto_renewal_until, str(a_learning_container.auto_renewal_until+1)[-2:])
        return "{}-{}".format(start_yr, end_year)
    else:
        if a_learning_container.start_year and not a_learning_container.auto_renewal_until:
            return "{} {}-{}".format(_('since'), a_learning_container.start_year,str(a_learning_container.start_year+1)[-2:])
        else:
            return "-"
