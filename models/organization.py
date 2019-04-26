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
from django.db import models
from django.core.exceptions import ObjectDoesNotExist, ValidationError, NON_FIELD_ERRORS
from osis_common.models.serializable_model import SerializableModel, SerializableModelAdmin
from internship.models.enums import organization_report_fields
from django.utils.translation import ugettext_lazy as _


class OrganizationAdmin(SerializableModelAdmin):
    list_display = ('reference', 'name', 'acronym', 'cohort', 'location', 'postal_code', 'city', 'country')
    fieldsets = ((None, {'fields': ('name', 'acronym', 'reference', 'website', 'phone', 'location', 'postal_code',
                                    'city', 'country', 'cohort')}),)
    search_fields = ['acronym', 'name', 'reference']
    list_filter = ('cohort',)


class Organization(SerializableModel):
    name = models.CharField(max_length=255)
    acronym = models.CharField(max_length=15, blank=True)
    website = models.URLField(max_length=255, blank=True, null=True)
    reference = models.CharField(max_length=30, blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    country = models.ForeignKey('reference.Country', blank=True, null=True, on_delete=models.CASCADE)
    cohort = models.ForeignKey('internship.Cohort', on_delete=models.CASCADE)

    report_period = models.IntegerField(default=1, blank=True, null=True)
    report_start_date = models.IntegerField(default=2, blank=True, null=True)
    report_end_date = models.IntegerField(default=3, blank=True, null=True)
    report_last_name = models.IntegerField(default=4, blank=True, null=True)
    report_first_name = models.IntegerField(default=5, blank=True, null=True)
    report_gender = models.IntegerField(default=6, blank=True, null=True)
    report_specialty = models.IntegerField(default=7, blank=True, null=True)
    report_birthdate = models.IntegerField(default=8, blank=True, null=True)
    report_email = models.IntegerField(default=9, blank=True, null=True)
    report_noma = models.IntegerField(default=10, blank=True, null=True)
    report_phone = models.IntegerField(default=11, blank=True, null=True)
    report_address = models.IntegerField(default=12, blank=True, null=True)
    report_postal_code = models.IntegerField(default=13, blank=True, null=True)
    report_city = models.IntegerField(default=14, blank=True, null=True)

    class Meta:
        unique_together = ("reference", "cohort")

    def clean(self):
        self.clean_duplicate_sequence()

    def clean_duplicate_sequence(self):
        report = {field: value for field, value in vars(self).items() if "report_" in field and value is not None}
        report_values = [value for field, value in report.items()]
        duplicates = set([x for x in report_values if report_values.count(x) > 1])
        keys = [field for field, value in report.items() if value in duplicates]
        for k in keys:
            raise ValidationError({k: _("Duplicated sequence in report")})

    def report_sequence(self):
        """ Returns only the report fields that are numered and ordered as numered."""
        sequence = [None, None, None, None, None, None, None,
                    None, None, None, None, None, None, None]

        for field_name in organization_report_fields.REPORT_FIELDS:
            field = getattr(self, "report_{}".format(field_name))
            if field:
                sequence[field - 1] = field_name

        return filter(lambda i: i is not None, sequence)

    def unique_error_message(self, model_class, unique_check):
        if model_class == type(self) and unique_check == ('reference', 'cohort'):
            return _('A hospital with the same reference already exists in this cohort')
        else:
            return super(Organization, self).unique_error_message(model_class, unique_check)

    def __str__(self):
        return self.name


def search(**kwargs):
    kwargs = {k: v for k, v in kwargs.items() if v}
    return Organization.objects.filter(**kwargs).select_related()


def get_by_id(organization_id):
    try:
        return Organization.objects.get(pk=organization_id)
    except ObjectDoesNotExist:
        return None


def find_by_cohort(cohort):
    return Organization.objects.filter(cohort=cohort).order_by("reference")


def find_by_reference(cohort, reference):
    str_reference = str(reference).zfill(2)
    return Organization.objects.filter(cohort=cohort).filter(reference=str_reference)


def get_hospital_error(cohort):
    try:
        return Organization.objects.filter(cohort=cohort).get(reference=999)
    except ObjectDoesNotExist:
        return None


def sort_organizations(organizations):
    """
        Function to sort the organization by the reference
        Param:
            sort_organizations : list of organizations to sort
        Get the reference of the organization, transform and sort by the int key
        Recreate the list with the reference research
    """
    tab = []
    number_ref = []
    for organization in organizations:
        if organization is not None:
            number_ref.append(organization.reference)
    if number_ref:
        number_ref = sorted(number_ref, key=int)
        for i in number_ref:
            organization = search(reference=i)
            tab.append(organization[0])
    return tab
