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
from django import forms


class LearningUnitSpecificationsForm(forms.Form):
    learning_unit_year_id = forms.CharField(widget=forms.HiddenInput(), required=True)
    language = forms.CharField(widget=forms.HiddenInput(), required=True)
    themes = forms.CharField(widget=forms.Textarea())
    skills_to_be_acquired = forms.CharField(widget=forms.Textarea())
    prerequisite = forms.CharField(widget=forms.Textarea())

    def __init__(self, learning_unit_year, language, *args, **kwargs):
        super(LearningUnitSpecificationsForm, self).__init__(*args, **kwargs)
        self.fields['learning_unit_year_id'].initial = learning_unit_year.id
        self.fields['language'].initial = language
        self.refresh_data(learning_unit_year, language)
        self._all_field_read_only()

    def refresh_data(self, learning_unit_year, language):
       pass

    def _all_field_read_only(self):
        # Actually it is read only screen
        for field in self.fields.values():
            field.widget.attrs.update({'readonly':True, 'style': 'border:0;outline-style:none;'})

