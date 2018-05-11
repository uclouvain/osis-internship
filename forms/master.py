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
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from reference.models import country
from base.forms import bootstrap
from internship.models import internship_master, organization


class MasterForm(bootstrap.BootstrapModelForm):
    country = forms.ModelChoiceField(queryset=country.find_all(), required=False)

    def clean(self):
        cleaned_data = super().clean()
        birth_date = cleaned_data.get("birth_date")
        if birth_date is not None and birth_date > timezone.now().date():
            raise forms.ValidationError(_("birth_date_before_today"))

    class Meta:
        model = internship_master.InternshipMaster
        fields = ['first_name', 'last_name', 'civility', 'gender', 'email', 'email_private', 'location',
                  'postal_code', 'city', 'country', 'phone', 'phone_mobile', 'birth_date', 'start_activities']
        widgets = {
            'birth_date': forms.DateInput(
                format="%Y-%m-%d",
                attrs={
                    'type': 'date',
                    'max': timezone.now().date().strftime('%Y-%m-%d')
                }),
            'start_activities': forms.DateInput(format="%Y-%m-%d", attrs={'type': 'date'})
        }