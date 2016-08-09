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
from django.forms import ModelForm
from internship.models import InternshipChoice, InternshipOffer, Organization, Period, InternshipMaster, InternshipSpeciality
from functools import partial
DateInput = partial(forms.DateInput, {'class': 'datepicker'})


class InternshipChoiceForm(ModelForm):
    class Meta :
        model = InternshipChoice
        fields = ['organization', 'speciality', 'student', 'choice']

class InternshipOfferForm(ModelForm):
    class Meta :
        model = InternshipOffer
        fields = ['organization', 'speciality', 'title', 'maximum_enrollments', 'selectable']

class OrganizationForm(ModelForm):
    file = forms.FileField()
    class Meta:
        model = Organization
        fields = ['acronym', 'name', 'website', 'reference']

class InternshipSpecialityForm(ModelForm):
    file = forms.FileField()
    class Meta:
        model = InternshipSpeciality
        fields = ['learning_unit', 'name', 'mandatory']

class PeriodForm(ModelForm):
    class Meta:
        model = Period
        fields = ['name', 'date_start', 'date_end']
        widgets = {'date_start': forms.DateInput(format='%d/%m/%Y'),
                'date_start': forms.DateInput(format='%d/%m/%Y'),
        }

class InternshipMasterForm(ModelForm):
    file = forms.FileField()
    class Meta:
        model = InternshipMaster
        fields = ['organization', 'first_name', 'last_name', 'reference', 'civility', 'type_mastery', 'speciality']
