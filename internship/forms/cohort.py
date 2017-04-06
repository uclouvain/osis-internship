from django import forms
from django.forms import TextInput

from internship.models.cohort import Cohort


class DateInput(TextInput):
    input_type = 'date'


class CohortForm(forms.ModelForm):
    publication_start_date = forms.DateField(widget=DateInput)
    subscription_start_date = forms.DateField(widget=DateInput)
    subscription_end_date = forms.DateField(widget=DateInput)

    class Meta:
        model = Cohort
        fields = [
            'name',
            'description',
            'free_internships_number',
            'publication_start_date',
            'subscription_start_date',
            'subscription_end_date'
        ]

    def __init__(self, *args, **kwargs):
        super(forms.ModelForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })

        self.fields['publication_start_date'].widget.attrs.update({
            'placeholder': "AAAA-MM-JJ",
        })