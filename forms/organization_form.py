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
from collections import Counter

from django import forms
from django.utils.translation import ugettext_lazy as _
from reference.models import country

from base.forms.bootstrap import BootstrapModelForm
from internship.models.organization import Organization


class OrganizationForm(BootstrapModelForm):
    country = forms.ModelChoiceField(queryset=country.find_all(), required=False)

    def clean(self):
        cleaned_data = super().clean()
        report = {field: value for field, value in cleaned_data.items() if "report_" in field and value is not None}
        report_values = [value for field, value in report.items()]
        duplicates = set([x for x in report_values if report_values.count(x) > 1])
        keys = [field for field, value in report.items() if value in duplicates]
        for k in keys:
            self.add_error(k, _("duplicate_report_sequence"))

    class Meta:
        model = Organization
        fields = ['name', 'website', 'reference', 'location', 'postal_code', 'city', 'country', 'report_period',
                  'report_start_date', 'report_end_date', 'report_last_name', 'report_first_name', 'report_gender',
                  'report_specialty', 'report_birthdate', 'report_email', 'report_noma', 'report_phone',
                  'report_address', 'report_postal_code', 'report_city']
