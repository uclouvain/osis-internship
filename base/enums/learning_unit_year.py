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

#Global variable

#Errors handling on form
error_required = 'This field is required'
error_invalid = 'Enter a valid value'
error_academic_year_required = 'Please specify an academic year'
error_invalid_search = 'Invalid search - Please fill some information before executing a search.'

LEARNING_UNIT_YEARS_ERRORS = (
    (error_required, _('This field is required')),
    (error_invalid, _('Enter a valid value')),
    (error_academic_year_required, _('Please specify an academic year')),
    (error_invalid_search, _('Invalid search - Please fill some information before executing a search.'))
)

#Status in model learning_unit_year
status_none = ""
status_valid = "Valid"
status_invalid = "Invalid"

LEARNING_UNIT_YEAR_STATUS = (
    (status_none, _('None')),
    (status_valid, _('Valid')),
    (status_invalid, _('Invalid'))
)

#Types in model learning_unit_year
type_none = ""
type_course = "Course"
type_master_thesis = "Master thesis"
type_internship = "Internship"

LEARNING_UNIT_YEAR_TYPES = (
    (type_none, _('None')),
    (type_course, _('Course')),
    (type_master_thesis, _('Master thesis')),
    (type_internship, _('Internship'))
)