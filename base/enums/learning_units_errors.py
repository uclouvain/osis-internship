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

from django.utils.translation import ugettext_lazy as _

REQUIRED = 'This field is required'
INVALID = 'Enter a valid value'
INVALID_SEARCH = 'Invalid search - Please fill some information before executing a search.'
ACADEMIC_YEAR_REQUIRED = 'Please specify an academic year'
ACADEMIC_YEAR_WITH_ACRONYM = 'Please specify an academic year or enter a valid acronym.'

LEARNING_UNIT_YEARS_ERRORS = (
    (REQUIRED, _(REQUIRED)),
    (INVALID, _(INVALID)),
    (INVALID_SEARCH, _(INVALID_SEARCH)),
    (ACADEMIC_YEAR_REQUIRED, _(ACADEMIC_YEAR_REQUIRED)),
    (ACADEMIC_YEAR_WITH_ACRONYM, _(ACADEMIC_YEAR_WITH_ACRONYM))
)