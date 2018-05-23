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
from django.forms import ModelForm

from base.forms.bootstrap import BootstrapModelForm
from internship.models.period import Period
from django import forms
from django.utils.translation import ugettext_lazy as _

class PeriodForm(BootstrapModelForm):

    def clean(self):
        cleaned_data = super().clean()
        date_start = cleaned_data.get("date_start")
        date_end = cleaned_data.get("date_end")
        if all([date_start, date_end]):
            if date_start >= date_end:
                self.add_error("date_start", _("start_before_end"))

    class Meta:
        model = Period
        fields = ['name', 'date_start', 'date_end']
        widgets = {
            'date_start': forms.DateInput(format="%Y-%m-%d", attrs={'type': 'date'}),
            'date_end': forms.DateInput(format="%Y-%m-%d", attrs={'type': 'date'})
        }
