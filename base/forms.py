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
from django.utils.translation import ugettext as trans
from django import forms
from django.forms import ModelForm
from admission import models as admission
from django.utils.translation import ugettext_lazy as _

from base import models as mdl


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class ScoreFileForm(forms.Form):
    file = forms.FileField(error_messages={'required': _('no_file_submitted')})

    def clean_file(self):
        file = self.cleaned_data['file']
        content_type = file.content_type.split('/')[1]
        valid_content_type = 'vnd.openxmlformats-officedocument.spreadsheetml.sheet' in content_type
        if ".xlsx" not in file.name or not valid_content_type:
            self.add_error('file', forms.ValidationError(_('file_must_be_xlsx'), code='invalid'))
        return file


class OrganizationForm(ModelForm):
    class Meta:
        model = mdl.organization.Organization
        fields = ['acronym', 'name', 'website', 'reference']


class AcademicCalendarForm(ModelForm):
    class Meta:
        model = mdl.academic_calendar.AcademicCalendar
        exclude = ['external_id', 'changed']

    def is_valid(self):
        valid = super(AcademicCalendarForm, self).is_valid()
        if not valid:
            return valid
        off_year_calendar_max = mdl.offer_year_calendar.get_max_end_date(self.instance.id)
        if off_year_calendar_max and self.cleaned_data['end_date'] < off_year_calendar_max.end_date:
            error_msg = "%s." % (trans('academic_calendar_offer_year_calendar_end_date_error')
                                 % (off_year_calendar_max.end_date.strftime('%d/%m/%Y'),
                                    off_year_calendar_max.offer_year.acronym))
            self._errors['end_date'] = error_msg
            return False
        return True


class OfferYearCalendarForm(ModelForm):
    start_date = forms.DateField(widget=forms.DateInput(format='%d/%m/%Y'),
                                 input_formats=('%d/%m/%Y', ),
                                 required=True)
    end_date = forms.DateField(widget=forms.DateInput(format='%d/%m/%Y'),
                               input_formats=('%d/%m/%Y', ),
                               required=True)

    class Meta:
        model = mdl.offer_year_calendar.OfferYearCalendar
        fields = ['offer_year', 'start_date', 'end_date', 'customized']


class OfferFormForm(ModelForm):
    class Meta:
        model = admission.form.Form
        fields = ['offer_year', 'title', 'description']


class OfferQuestionForm(ModelForm):
    class Meta:
        model = admission.question.Question
        fields = ['id', 'label', 'description', 'type', 'order', 'required', 'form']


class MyMessageForm(forms.Form):
    selected = forms.BooleanField(initial=False, required=False)
    subject = forms.CharField(required=False)
    created = forms.DateTimeField(required=False)
    read = forms.BooleanField(initial=False, required=False)
    id = forms.IntegerField()


class MyMessageActionForm(forms.Form):
    ACTIONS = (('MARK_AS_READ', _('mark_selected_as_read')), ('DELETE', _('delete_selected')))
    action = forms.ChoiceField(required=False, choices=ACTIONS, initial=None)
