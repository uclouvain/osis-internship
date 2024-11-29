##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.utils.translation import gettext as _

from internship.models.cohort import Cohort
from internship.models.organization import Organization
from reference.models.country import Country

YES_NO_CHOICES = (
    (False, _('No')),
    (True, _('Yes'))
)


class OrganizationForm(forms.ModelForm):
    country = forms.ModelChoiceField(
        queryset=Country.objects.order_by('name'), required=False, label=_('Country')
    )
    cohort = forms.ModelChoiceField(
        queryset=Cohort.objects.all(), required=False, disabled=True, label=_('Cohort')
    )
    fake = forms.TypedChoiceField(
        coerce=lambda x: x == 'True',
        required=False,
        choices=YES_NO_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
        label=_('Fake')
    )

    def __init__(self, *args, **kwargs):
        super(OrganizationForm, self).__init__(*args, **kwargs)
        self.fields['location'].label = _('Street and number')

    class Meta:
        model = Organization
        fields = ['name', 'website', 'reference', 'location', 'postal_code', 'city', 'country', 'report_period',
                  'report_start_date', 'report_end_date', 'report_last_name', 'report_first_name', 'report_gender',
                  'report_specialty', 'report_birthdate', 'report_email', 'report_noma', 'report_phone',
                  'report_address', 'report_postal_code', 'report_city', 'cohort', 'fake']
