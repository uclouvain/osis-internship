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
from base.enums import learning_unit_year_status
from base.enums import learning_unit_year_types


class LearningUnitYearForm(forms.Form):
    academic_year = forms.CharField(max_length=10, required=False)
    acronym = forms.CharField(widget=forms.TextInput(attrs={'size': '10'}), max_length=20, required=False)
    keyword = forms.CharField(widget=forms.TextInput(attrs={'size': '10'}), max_length=20, required=False)
    type = forms.CharField(
        widget=forms.Select(choices=learning_unit_year_types.LEARNING_UNIT_YEAR_TYPES),
        required=False
    )
    status = forms.CharField(
        widget=forms.Select(choices=learning_unit_year_status.LEARNING_UNIT_YEAR_STATUS),
        required=False
    )

    def clean(self):
        minimal_inputs_satisfied = ''
        clean_data = self.cleaned_data
        for cd_key, cd_value in clean_data.items():
            if cd_value == 'NONE' or cd_value == '0':
                clean_data[cd_key] = ''
            minimal_inputs_satisfied = minimal_inputs_satisfied+clean_data[cd_key]

        if not minimal_inputs_satisfied:
            raise ValidationError('LU_ERRORS_INVALID_SEARCH')
        elif not clean_data.get('academic_year'):
            check_when_academic_year_is_all(clean_data.get('acronym'))
        return clean_data

    def set_academic_years_all(self):
        academic_years_all = True if not self.cleaned_data.get('academic_year') else False
        return academic_years_all

    def get_learning_units(self):
        clean_data = self.cleaned_data
        if not clean_data.get('academic_year'):
            learning_units = check_when_academic_year_is_all(clean_data.get('acronym'))
        else:
            learning_units = mdl.learning_unit_year.search(academic_year_id=clean_data.get('academic_year'),
                                                           acronym=clean_data.get('acronym'),
                                                           title=clean_data.get('keyword'),
                                                           type=clean_data.get('type'),
                                                           status=clean_data.get('status'))
        return learning_units

    def get_academic_year(self):
        academic_year = 0 if not self.cleaned_data.get('academic_year') else self.cleaned_data.get('academic_year')
        return academic_year


def check_when_academic_year_is_all(acronym):
    if acronym:
        learning_units = check_learning_units_with_acronym(acronym)
        return learning_units
    elif not acronym:
        raise ValidationError('LU_ERRORS_ACADEMIC_YEAR_REQUIRED')


def check_learning_units_with_acronym(acronym):
    learning_units = mdl.learning_unit_year.find_by_acronym(acronym)

    if not learning_units:
        raise ValidationError('LU_ERRORS_YEAR_WITH_ACRONYM')

    return learning_units
