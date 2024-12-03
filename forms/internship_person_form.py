##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2020 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.utils.translation import gettext_lazy as _

from base.models.enums import person_source_type
from base.models.person import Person


class InternshipPersonForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(InternshipPersonForm, self).__init__(*args, **kwargs)
        self.fields['last_name'].required = True

        self.fields['last_name'].label = _('Last name')
        self.fields['first_name'].label = _('First name')
        self.fields['birth_date'].label = _('Birth date')
        self.fields['gender'].label = _('Gender')
        self.fields['phone'].label = _('Phone')
        self.fields['phone_mobile'].label = _('Phone mobile')

        # disable fields for instance source not internship
        if self.instance.pk and self.instance.source != person_source_type.INTERNSHIP:
            self.disable_all_fields()

    def disable_all_fields(self):
        for field in self.fields.values():
            field.disabled = True

    def save(self, *args, **kwargs):
        person = super(InternshipPersonForm, self).save(commit=False)
        if person.pk is None:
            person.source = person_source_type.INTERNSHIP
        person.save()
        return person

    class Meta:
        model = Person
        fields = [
            'last_name',
            'first_name',
            'gender',
            'birth_date',
            'email',
            'phone',
            'phone_mobile'
        ]
        widgets = {
            'birth_date': forms.DateInput(format="%Y-%m-%d", attrs={'type': 'date'}),
            'start_activities': forms.DateInput(format="%Y-%m-%d", attrs={'type': 'date'})
        }
