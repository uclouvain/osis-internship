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
from django.forms import CheckboxSelectMultiple

from internship.models import internship_speciality
from internship.models.internship import Internship
from internship.models.internship_modality_apd import InternshipModalityApd, APDS_DESCRIPTIONS
from internship.models.internship_modality_period import InternshipModalityPeriod
from internship.models.internship_score import APD_NUMBER
from internship.models.period import Period
from django.utils.translation import gettext_lazy as _

def _apd_choices():
    return [(index, f"APD {index} : {APDS_DESCRIPTIONS[str(index)]}") for index in range(1, APD_NUMBER + 1)]

class InternshipForm(forms.ModelForm):

    periods = forms.ModelMultipleChoiceField(
        queryset=Period.objects.all(),
        required=False,
        widget=CheckboxSelectMultiple(),
        help_text=_(
            'Select which period should be exclusively filled for this modality.'
            ' No selection means there is no constraint on the period.'
        )
    )

    apds = forms.MultipleChoiceField(
        choices=_apd_choices(),
        required=False,
        widget=CheckboxSelectMultiple(),
        help_text=_(
            'Select which APDs are required for this modality.'
        )
    )

    class Meta:
        model = Internship
        fields = [
            'name',
            'speciality',
            'length_in_periods',
            'position',
        ]

    def __init__(self, *args, **kwargs):
        super(InternshipForm, self).__init__(*args, **kwargs)
        cohort_id = kwargs['instance'].cohort_id

        self.fields['speciality'].queryset = internship_speciality.find_by_cohort(cohort_id)

        self.fields['periods'].queryset = Period.objects.filter(cohort_id=cohort_id)
        self.fields['periods'].initial = InternshipModalityPeriod.objects.filter(
            internship=kwargs['instance']
        ).values_list('period_id', flat=True)

        self.fields['apds'].choices = _apd_choices()
        self.fields['apds'].initial = [apd for apd in InternshipModalityApd.objects.filter(
            internship=kwargs['instance']
        ).values_list('apd', flat=True)]

    def save(self, commit=True):
        instance = super().save(commit)

        # delete existing modality periods for instance
        InternshipModalityPeriod.objects.filter(internship=instance).delete()

        # recreate according to data received
        InternshipModalityPeriod.objects.bulk_create(
            InternshipModalityPeriod(internship=instance, period=period) for period in self.cleaned_data['periods']
        )

        # delete existing modality apds for instance
        InternshipModalityApd.objects.filter(internship=instance).delete()

        # recreate according to data received
        InternshipModalityApd.objects.bulk_create(
            InternshipModalityApd(internship=instance, apd=apd) for apd in self.cleaned_data['apds']
        )

        return instance
