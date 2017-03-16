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
from django.core.exceptions import ValidationError
from base.enums import learning_unit_year

class LearningUnitYearForm(forms.Form):

    academic_year=forms.CharField(max_length=20, required=False)
    acronym = forms.CharField(max_length=20, required=False)
    keyword = forms.CharField(max_length=20, required=False)
    type = forms.CharField(
        widget=forms.Select(choices=learning_unit_year.LEARNING_UNIT_YEAR_TYPES),
        required=False
    )
    status=forms.CharField(
        widget=forms.Select(choices=learning_unit_year.LEARNING_UNIT_YEAR_STATUS),
        required=False
    )

    def clean(self):
        academic_year = self.cleaned_data.get('academic_year')
        acronym = self.cleaned_data.get('acronym').upper()
        keyword = self.cleaned_data.get('keyword')
        status = self.cleaned_data.get('status')
        type = self.cleaned_data.get('type')

        if (not acronym and not keyword and not status and not type):
            raise ValidationError(learning_unit_year.error_invalid_search)

        if (str(academic_year) == "-1"):
            if (acronym and not keyword and not type and not status):
                learning_units=mdl.learning_unit_year.find_by_acronym(acronym)
                if not learning_units:
                    self.add_error('acronym', learning_unit_year.error_academic_year_required)
            if (not acronym and keyword and not type and not status):
                self.add_error('keyword', learning_unit_year.error_academic_year_required)
            if (not acronym and not keyword and not type and status):
                self.add_error('status', learning_unit_year.error_academic_year_required)
            if (not acronym and not keyword and type and not status):
                self.add_error('type', learning_unit_year.error_academic_year_required)
            if (not acronym and not keyword and type and status):
                self.add_error('type', learning_unit_year.error_academic_year_required)
        return self.cleaned_data