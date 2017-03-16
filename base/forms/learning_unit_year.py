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
        cd=self.cleaned_data
        academic_year = cd.get('academic_year')
        acronym = cd.get('acronym').upper()
        keyword = cd.get('keyword')
        status = cd.get('status')
        type = cd.get('type')

        if (not acronym and not keyword and not status and not type):
            raise ValidationError(learning_unit_year.error_invalid_search)
        elif (str(academic_year) == "-1"):
            check_when_academic_year_is_all(acronym,keyword,status,type)
        return cd

    def set_academic_years_all(self):
        academic_year = self.cleaned_data.get('academic_year')
        if academic_year=="-1":
            academic_years_all=1
        else:
            academic_years_all=0
        return academic_years_all

    def get_learning_units(self):
        academic_year = self.cleaned_data.get('academic_year')
        acronym = self.cleaned_data.get('acronym').upper()
        keyword = self.cleaned_data.get('keyword')
        status = self.cleaned_data.get('status')
        type = self.cleaned_data.get('type')
        if (academic_year=="-1" and acronym):
            learning_units=mdl.learning_unit_year.find_by_acronym(acronym)
        else:
            if (academic_year=="-1"):
                learning_units = mdl.learning_unit_year.search(academic_year_id=None,acronym=acronym,title=keyword,type=type,status=status)
            else:
                learning_units = mdl.learning_unit_year.search(academic_year_id=academic_year,acronym=acronym,title=keyword,type=type,status=status)
        return learning_units

    def get_academic_year(self):
        academic_year = self.cleaned_data.get('academic_year')
        return academic_year

def check_when_academic_year_is_all(acronym,keyword,status,type):
    if (acronym and not keyword and not type and not status):
        check_learning_units_with_acronym(acronym)
    elif (not acronym):
        check_when_acronym_is_none(keyword,type,status)

def check_learning_units_with_acronym(acronym):
        learning_units=mdl.learning_unit_year.find_by_acronym(acronym)
        if not learning_units:
           raise ValidationError(learning_unit_year.error_academic_year_with_acronym)

def check_when_acronym_is_none(keyword,type,status):
    if (keyword and (not type or not status)):
        raise ValidationError(learning_unit_year.error_academic_year_required)