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
from dissertation.models.proposition_dissertation import PropositionDissertation
from dissertation.models.adviser import Adviser
from dissertation.models.offer_proposition import OfferProposition

class AdviserForm(ModelForm):
    class Meta:
        model = Adviser
        fields = ('email_accept','phone_accept','office_accept','comment')

class ManagerAdviserForm(ModelForm):
    class Meta:
        model = Adviser
        fields = ('email_accept','phone_accept','office_accept','comment')

class ManagerPropositionDissertationForm(ModelForm):
    class Meta:
        model = PropositionDissertation
        fields = ('author','visibility','title','description','type','level','collaboration','max_number_student','offer_proposition')
        widgets = {'offer_proposition': forms.CheckboxSelectMultiple()}

class PropositionDissertationForm(ModelForm):
    class Meta:
        model = PropositionDissertation
        fields = ('author','visibility','title','description','type','level','collaboration','max_number_student','offer_proposition')
        widgets = {'author': forms.HiddenInput(),'offer_proposition': forms.CheckboxSelectMultiple()}

class OfferPropositionForm(ModelForm):
    class Meta:
        model = OfferProposition
        fields = ('title','offer_year','adviser_reader','commission_validation','commission_readers','evaluation_first_cicle','visibility_commission_readers')
        widgets = {'offer_proposition': forms.CheckboxSelectMultiple()}
