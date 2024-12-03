from django import forms
from django.db.models import Q
from django.forms import Form
from django.utils.translation import gettext as _

from internship.models.internship_speciality import InternshipSpeciality
from internship.models.internship_student_information import InternshipStudentInformation
from internship.models.organization import Organization
from internship.models.period import get_effective_periods, get_subcohorts_periods, Period


class ScoresFilterForm(Form):

    EMPTY_YES_NO_CHOICES = (
        (None, '-'),
        (True, _('Yes')),
        (False, _('No')),
    )

    free_text = forms.CharField(
        max_length=100,
        required=False,
        label=_('In all fields'),
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    period = forms.ModelChoiceField(
        queryset=None,
        required=False,
        empty_label=None,
        widget=forms.SelectMultiple(attrs={"class": "form-select", "multiple": "multiple"})
    )

    specialty = forms.ModelChoiceField(
        queryset=None,
        required=False,
        empty_label='-',
        widget=forms.Select(attrs={"class": "form-select"})
    )

    organization = forms.ModelChoiceField(
        queryset=None,
        required=False,
        empty_label='-',
        widget=forms.Select(attrs={"class": "form-select"})
    )

    yes_no_typed_choice_field = forms.TypedChoiceField(
        coerce=lambda x: x == 'True',
        required=False,
        choices=EMPTY_YES_NO_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"})
    )

    all_grades_submitted_filter = yes_no_typed_choice_field
    evaluations_submitted_filter = yes_no_typed_choice_field
    all_apds_validated_filter = yes_no_typed_choice_field

    show_apds_validation = forms.BooleanField(
        required=False,
        initial=False
    )

    def __init__(self, *args, **kwargs):
        cohort = kwargs.pop('cohort')
        super(ScoresFilterForm, self).__init__(*args, **kwargs)

        if cohort.is_parent:
            cohorts = cohort.subcohorts.all()
            self.fields['period'].queryset = Period.objects.filter(cohort__in=cohorts).order_by('date_start')
            self.fields['specialty'].queryset = InternshipSpeciality.objects.filter(
                cohort__in=cohorts
            ).order_by('name').distinct('name')
            self.fields['organization'].queryset = Organization.objects.filter(
                cohort__in=cohorts
            ).order_by('reference').distinct('reference')
        else:
            self.fields['period'].queryset = cohort.period_set.all().order_by('date_start')
            self.fields['specialty'].queryset = cohort.internshipspeciality_set.order_by('name')
            self.fields['organization'].queryset = cohort.organization_set.order_by('reference')

        # disable clean on periods to retrieve periods pk
        self.fields['period'].clean = lambda x: x

        self.fields['organization'].label_from_instance = self.label_from_organization

    def get_students(self, cohort):
        free_text = self.cleaned_data.get('free_text')

        if cohort.is_parent:
            qs = InternshipStudentInformation.objects.filter(
                cohort__in=cohort.subcohorts.all()
            ).select_related('person')
        else:
            qs = cohort.internshipstudentinformation_set.all().select_related(
                'person'
            )

        if free_text:
            qs = search_students_with_free_text(free_text, qs)

        return qs.distinct('person_id')

    def get_periods(self, cohort):
        periods_filter = [pk for pk in self.data.getlist('period') if pk != '']
        periods = get_subcohorts_periods(cohort) if cohort.is_parent else get_effective_periods(cohort.id)
        if periods_filter:
            periods = [p for p in periods if str(p.pk) in periods_filter]
        return periods

    def get_specialties(self, cohort):
        specialty = self.cleaned_data.get('specialty')
        if cohort.is_parent:
            subcohorts = cohort.subcohorts.all()
            if specialty:
                qs = InternshipSpeciality.objects.filter(cohort__in=subcohorts, name=specialty.name)
            else:
                qs = InternshipSpeciality.objects.filter(cohort__in=subcohorts)
        else:
            if specialty:
                qs = cohort.internshipspeciality_set.filter(pk=specialty.pk)
            else:
                qs = cohort.internshipspeciality_set.all()
        return qs

    def get_organizations(self, cohort):
        organization = self.cleaned_data.get('organization')
        if cohort.is_parent:
            subcohorts = cohort.subcohorts.all()
            if organization:
                qs = Organization.objects.filter(cohort__in=subcohorts, reference=organization.reference)
            else:
                qs = Organization.objects.filter(cohort__in=subcohorts)
        else:
            if organization:
                qs = cohort.organization_set.filter(pk=organization.pk)
            else:
                qs = cohort.organization_set.all()
        return qs

    def get_all_grades_submitted_filter(self):
        return self.get_filter('all_grades_submitted_filter')

    def get_evaluations_submitted_filter(self):
        return self.get_filter('evaluations_submitted_filter')

    def get_all_apds_validated_filter(self):
        return self.get_filter('all_apds_validated_filter')

    def get_filter(self, filter_name):
        filter = self.cleaned_data.get(filter_name)
        if filter == "":
            return None
        return filter

    def label_from_organization(self, obj):
        return f"{obj.reference} - {obj.name}"


def search_students_with_free_text(free_text, qs):
    qs = qs.filter(
        Q(person__first_name__unaccent__icontains=free_text) |
        Q(person__last_name__unaccent__icontains=free_text)
    )
    return qs
