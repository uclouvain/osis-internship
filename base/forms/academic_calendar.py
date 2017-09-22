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
from operator import itemgetter

from django.utils.translation import ugettext_lazy as _
from django import forms
from django.db.models.fields import BLANK_CHOICE_DASH


from base.forms import bootstrap
from base.models import academic_calendar, offer_year_calendar, academic_year
from base.models.enums import academic_calendar_type


class AcademicCalendarForm(bootstrap.BootstrapModelForm):
    REFERENCE_CHOICE_FIELD = BLANK_CHOICE_DASH + \
        sorted([(a, _(b)) for (a, b) in academic_calendar_type.ACADEMIC_CALENDAR_TYPES],
               key=itemgetter(1))

    academic_year = forms.ModelChoiceField(queryset=academic_year.AcademicYear.objects.all().order_by('year'),
                                           widget=forms.Select(), empty_label=None)
    reference = forms.ChoiceField(choices=REFERENCE_CHOICE_FIELD, required=False)

    class Meta:
        model = academic_calendar.AcademicCalendar
        exclude = ['external_id', 'changed']

    def save(self, commit=True):
        instance = super(AcademicCalendarForm, self).save(commit=False)
        if commit:
            instance.save(functions=[offer_year_calendar.save_from_academic_calendar])
        return instance

    def end_date_gt_last_offer_year_calendar_end_date(self):
        off_year_calendar_max = offer_year_calendar.find_latest_end_date_by_academic_calendar(self.instance.id)
        date_format = str(_('date_format'))

        if off_year_calendar_max and self.cleaned_data['end_date'] \
                and self.cleaned_data['end_date'] < off_year_calendar_max.end_date:
            error_msg = "%s." % (_('academic_calendar_offer_year_calendar_end_date_error')
                                 % (self.instance.title,
                                    off_year_calendar_max.end_date.strftime(date_format),
                                    self.instance.title,
                                    off_year_calendar_max.offer_year.acronym))
            self._errors['end_date'] = error_msg
            return False
        return True

    def end_date_gt_start_date(self):
        if self.cleaned_data['end_date'] <= self.cleaned_data['start_date']:
            self._errors['start_date'] = _('start_date_must_be_lower_than_end_date')
            return False
        return True

    def is_valid(self):
        return super(AcademicCalendarForm, self).is_valid() \
            and self.start_date_and_end_date_are_set() \
            and self.end_date_gt_last_offer_year_calendar_end_date() \
            and self.end_date_gt_start_date()

    def start_date_and_end_date_are_set(self):
        if not self.cleaned_data.get('end_date') or not self.cleaned_data.get('start_date'):
            error_msg = "{0}".format(_('dates_mandatory_error'))
            self._errors['start_date'] = error_msg
            return False
        return True
