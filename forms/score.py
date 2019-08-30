from django import forms
from django.db.models import Q
from django.forms import Form
from django.utils.translation import gettext as _

from internship.models.internship_student_information import InternshipStudentInformation
from internship.models.period import Period


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

    score_filter = forms.TypedChoiceField(
        coerce=lambda x: x == 'True',
        required=False,
        choices=YES_NO_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"})
    )

    def __init__(self, *args, **kwargs):
        cohort = kwargs.pop('cohort')
        super(ScoresFilterForm, self).__init__(*args, **kwargs)
        self.fields['period'].queryset = Period.objects.filter(cohort=cohort).order_by('date_start')

    def get_students(self, cohort):
        free_text = self.cleaned_data.get('free_text')

        qs = InternshipStudentInformation.objects.filter(cohort=cohort).select_related(
            'person'
        ).order_by('person__last_name')

        if free_text:
            qs = search_students_with_free_text(free_text, qs)

        return qs.distinct()

    def get_period(self, cohort):
        period = self.cleaned_data.get('period')
        qs = Period.objects.filter(cohort=cohort).order_by('date_start')
        if period:
            qs = [Period.objects.get(pk=period.pk)]
        return qs

    def get_score_filter(self):
        score_filter = self.cleaned_data.get('score_filter')
        if score_filter == "":
            return None
        return score_filter


def search_students_with_free_text(free_text, qs):
    qs = qs.filter(
        Q(person__first_name__unaccent__icontains=free_text) |
        Q(person__last_name__unaccent__icontains=free_text)
    )
    return qs
