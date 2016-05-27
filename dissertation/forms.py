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
from dissertation.models.adviser import Adviser
from dissertation.models.dissertation import Dissertation
from dissertation.models.offer_proposition import OfferProposition
from dissertation.models.proposition_dissertation import PropositionDissertation
from dissertation.models.dissertation_role import DissertationRole


class AdviserForm(ModelForm):
    class Meta:
        model = Adviser
        fields = ('available_by_email', 'available_by_phone', 'available_at_office', 'comment')


class DissertationForm(ModelForm):
    class Meta:
        model = Dissertation
        fields = ('title', 'author', 'offer_year_start', 'proposition_dissertation', 'description')


class PropositionDissertationForm(ModelForm):
    class Meta:
        model = PropositionDissertation
        fields = (
            'author', 'visibility', 'title', 'description', 'type', 'level', 'collaboration', 'max_number_student',
            'offer_proposition')
        widgets = {'author': forms.HiddenInput(), 'offer_proposition': forms.CheckboxSelectMultiple()}


class ManagerAdviserForm(ModelForm):
    class Meta:
        model = Adviser
        fields = ('available_by_email', 'available_by_phone', 'available_at_office', 'comment')


class ManagerDissertationForm(ModelForm):
    class Meta:
        model = Dissertation
        fields = ('title', 'author', 'offer_year_start', 'proposition_dissertation', 'description')


class ManagerDissertationRoleForm(ModelForm):
    class Meta:
        model = DissertationRole
        fields = (
            'dissertation', 'status', 'adviser')
        widgets = {'dissertation': forms.HiddenInput()}


class ManagerOfferPropositionForm(ModelForm):
    class Meta:
        model = OfferProposition
        fields = ('adviser_can_suggest_reader', 'validation_commission_exists', 'student_can_manage_readers',
                  'evaluation_first_year', 'readers_visibility_date_for_students', 'offer')
        widgets = {'offer': forms.HiddenInput(), 'offer_proposition': forms.CheckboxSelectMultiple()}


class ManagerPropositionDissertationForm(ModelForm):
    class Meta:
        model = PropositionDissertation
        fields = (
            'author', 'visibility', 'title', 'description', 'type', 'level', 'collaboration', 'max_number_student',
            'offer_proposition')
        widgets = {'offer_proposition': forms.CheckboxSelectMultiple()}
