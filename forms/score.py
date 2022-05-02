from django import forms
from django.db.models import Q
from django.forms import Form
from django.utils.translation import gettext as _

from internship.models.period import get_effective_periods


class ScoresFilterForm(Form):

    YES_NO_CHOICES = (
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
        empty_label='-',
        widget=forms.Select(attrs={"class": "form-control"})
    )

    specialty = forms.ModelChoiceField(
        queryset=None,
        required=False,
        empty_label='-',
        widget=forms.Select(attrs={"class": "form-control"})
    )

    organization = forms.ModelChoiceField(
        queryset=None,
        required=False,
        empty_label='-',
        widget=forms.Select(attrs={"class": "form-control"})
    )

    yes_no_typed_choice_field = forms.TypedChoiceField(
        coerce=lambda x: x == 'True',
        required=False,
        choices=YES_NO_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"})
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
        self.fields['period'].queryset = cohort.period_set.all().order_by('date_start')
        self.fields['specialty'].queryset = cohort.internshipspeciality_set.order_by('name')
        self.fields['organization'].queryset = cohort.organization_set.order_by('reference')

    def get_students(self, cohort):
        free_text = self.cleaned_data.get('free_text')

        qs = cohort.internshipstudentinformation_set.all().select_related(
            'person'
        ).order_by('person__last_name')

        if free_text:
            qs = search_students_with_free_text(free_text, qs)

        return qs.distinct()

    def get_period(self, cohort):
        period = self.cleaned_data.get('period')
        qs = get_effective_periods(cohort.id)  # exclude last period without grade associated
        if period:
            qs = qs.filter(pk=period.pk)
        return qs

    def get_specialty(self, cohort):
        specialty = self.cleaned_data.get('specialty')
        if specialty:
            qs = cohort.internshipspeciality_set.filter(pk=specialty.pk)
        else:
            qs = cohort.internshipspeciality_set.all()
        return qs

    def get_organization(self, cohort):
        organization = self.cleaned_data.get('organization')
        if organization:
            qs = cohort.organization_set.filter(pk=organization.pk)
        else:
            qs = cohort.organization_set.all()
        return qs

    def is_filtered_by_organization_or_specialty(self):
        return self.cleaned_data.get('organization') or self.cleaned_data.get('specialty')

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


def search_students_with_free_text(free_text, qs):
    qs = qs.filter(
        Q(person__first_name__unaccent__icontains=free_text) |
        Q(person__last_name__unaccent__icontains=free_text)
    )
    return qs
