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
from django import forms
from base import models as mdl
from base.enums import learning_unit_year_type
from base.enums import learning_unit_year_status

class LearningUnitYearForm(forms.Form):

    academic_year=forms.CharField(max_length=20, required=False)
    acronym = forms.CharField(max_length=20, required=False)
    keyword = forms.CharField(max_length=20, required=False)
    type = forms.CharField(
        widget=forms.Select(choices=learning_unit_year_type.LEARNING_UNIT_YEAR_TYPES),
        required=False
    )
    status=forms.CharField(
        widget=forms.Select(choices=learning_unit_year_status.LEARNING_UNIT_YEAR_STATUS),
        required=False
    )

    def clean(self):
        academic_year = self.cleaned_data.get('academic_year')
        if (str(academic_year) == "-1"):
            acronym = self.cleaned_data.get('acronym')
            keyword = self.cleaned_data.get('keyword')
            status = self.cleaned_data.get('status')
            type = self.cleaned_data.get('type')
            if (not acronym and not keyword and not status and not type):
                self.add_error('academic_year', "Please fill some information before executing a research")
                return False
            if (not keyword and not status and not type):
                self.add_error('acronym', "Please specify an academic year.")
                return False
            if (not acronym and not status and not type):
                self.add_error('keyword', "Please specify an academic year.")
                return False
            if (not acronym and not keyword and not type):
                self.add_error('status', "Please specify an academic year.")
                return False
            if (not acronym and not keyword and not status):
                self.add_error('type', "Please specify an academic year.")
                return False

    def clean_acronym(self):
        acronym = self.cleaned_data.get('acronym').upper()
        academic_year = self.cleaned_data.get('academic_year')
        if (acronym and str(academic_year) == "-1"):
            learning_units=mdl.learning_unit_year.find_by_acronym(acronym)
            if not learning_units:
                self.add_error('acronym', "If you dont specify an academic year, please enter a valid acronym.")
                return False
            else:
                return True