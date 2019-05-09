from django import forms
from django.db.models import Q
from django.utils.translation import gettext as _

from continuing_education.forms.search import BootstrapForm
from internship.models.internship_student_information import InternshipStudentInformation


class StudentsFilterForm(BootstrapForm):

    free_text = forms.CharField(max_length=100, required=False, label=_('In all fields'))

    def __init__(self, *args, **kwargs):
        super(StudentsFilterForm, self).__init__(*args, **kwargs)

    def get_students(self, cohort):
        free_text = self.cleaned_data.get('free_text')

        qs = InternshipStudentInformation.objects.filter(cohort=cohort).select_related(
            'person'
        ).order_by('person__last_name')

        if free_text:
            qs = search_students_with_free_text(free_text, qs)

        return qs.distinct()


def search_students_with_free_text(free_text, qs):
    qs = qs.filter(
        Q(person__first_name__icontains=free_text) |
        Q(person__last_name__icontains=free_text)
    )
    return qs
