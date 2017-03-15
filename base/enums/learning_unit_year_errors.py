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
#Eviter l'utilisation de variables pour la traduction:
#l’utilitaire de détection des chaînes à traduire de Django, django-admin makemessages, ne sera pas capable de trouver ces chaînes.
REQUIRED = 'This field is required'
INVALID = 'Enter a valid value'
ACADEMIC_YEAR_REQUIRED = 'Please specify an academic year'
INVALID_SEARCH = 'Invalid search - Please fill some information before executing a search.'

LEARNING_UNIT_YEARS_ERRORS = (
    (REQUIRED, _('This field is required')),
    (INVALID, _('Enter a valid value')),
    (ACADEMIC_YEAR_REQUIRED, _('Please specify an academic year')),
    (INVALID_SEARCH, _('Invalid search - Please fill some information before executing a search.'))
)