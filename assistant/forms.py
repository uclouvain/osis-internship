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
from django.forms import ModelForm, Textarea
from assistant import models as mdl
from assistant.models import academic_assistant


class MandateForm(ModelForm):
    comment = forms.CharField(
        required = False,
        widget = Textarea(attrs={'rows': '3', 'cols': '50'}))
    absences = forms.CharField(
        required = False, 
        widget = Textarea(attrs={'rows': '3', 'cols': '50'}))
    other_status = forms.CharField(
        required = False)
    renewal_type=forms.ChoiceField(choices= mdl.assistant_mandate.AssistantMandate.RENEWAL_TYPE_CHOICES)
    class Meta:
        model = mdl.assistant_mandate.AssistantMandate
        fields = ('comment','absences','other_status','renewal_type')
        
class HorizontalRadioRenderer(forms.RadioSelect.renderer):
    def render(self):
        return (u'\n'.join([u'%s\n' % w for w in self]))
            
class AssistantFormPart1(forms.Form):
    inscription = forms.ChoiceField(
            choices=academic_assistant.AcademicAssistant.PHD_INSCRIPTION_CHOICES,
            widget=forms.RadioSelect(renderer=HorizontalRadioRenderer)
            )
    expected_phd_date = forms.DateField(widget=forms.DateInput(format=('%d/%m/%Y'),
                               attrs={'placeholder':'dd/mm/yyyy'}), input_formats=('%d/%m/%Y'))
    phd_inscription_date = forms.DateField(widget=forms.DateInput(format=('%d/%m/%Y'),
                               attrs={'placeholder':'dd/mm/yyyy'}), input_formats=('%d/%m/%Y'))
    confirmation_test_date = forms.DateField(widget=forms.DateInput(format=('%d/%m/%Y'),
                               attrs={'placeholder':'dd/mm/yyyy'}), input_formats=('%d/%m/%Y')) 
    thesis_date = forms.DateField(widget=forms.DateInput(format=('%d/%m/%Y'),
                               attrs={'placeholder':'dd/mm/yyyy'}), input_formats=('%d/%m/%Y'))  
    supervisor = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'firstname.lastname@uclouvain.be', 'size':'30'}))
    external_functions = forms.CharField(widget=forms.Textarea(attrs={'cols':'40','rows':'2'}))
    external_contract = forms.CharField(widget=forms.Textarea(attrs={'cols':'40','rows':'2'}))
    justification = forms.CharField(widget=forms.Textarea(attrs={'cols':'40','rows':'2'}))  
