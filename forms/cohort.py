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
from django.forms import TextInput
from django.utils.translation import gettext_lazy as _

from internship.models import cohort
from internship.models.cohort import Cohort


class DateInput(TextInput):
    input_type = 'date'


class CohortForm(forms.ModelForm):
    publication_start_date = forms.DateField(widget=DateInput, required=False, label=_('Publication date'))
    subscription_start_date = forms.DateField(widget=DateInput, required=False, label=_('Enrolment start'))
    subscription_end_date = forms.DateField(widget=DateInput, required=False, label=_('Enrolment end'))
    originated_from = forms.ModelChoiceField(
        queryset=Cohort.objects.all(), empty_label="", required=False, label=_('Copy from cohort')
    )
    is_parent = forms.BooleanField(required=False, label=_('Is parent'))
    parent_cohort = forms.ModelChoiceField(
        queryset=Cohort.objects.filter(is_parent=True), empty_label="", required=False, label=_('Select parent cohort')
    )

    class Meta:
        model = cohort.Cohort
        fields = [
            'name',
            'description',
            'publication_start_date',
            'subscription_start_date',
            'subscription_end_date',
            'originated_from',
            'is_parent',
            'parent_cohort',
        ]
