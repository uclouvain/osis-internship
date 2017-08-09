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
from django import forms
from base import models as mdl
from django.utils.translation import ugettext_lazy as _


class LearningClassEditForm(forms.ModelForm):
    used_by = forms.BooleanField(required=False)

    class Meta:
        model = mdl.learning_class_year.LearningClassYear
        fields = ['description',]
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 1})
        }

    def __init__(self, *args, **kwargs):
        self.learning_unit_year = kwargs.pop('learning_unit_year', None)
        self.learning_component_year = kwargs.pop('learning_component_year', None)
        self.learning_class_year = kwargs.pop('learning_class_year', None)
        self.description = kwargs.get('description', None)
        self.used_by = kwargs.pop('used_by', None)
        self.message = kwargs.pop('message', None)
        self.title = '{} : {} {}'.format(_('classe'),
                                         self.learning_component_year.type_letter_acronym,
                                         self.learning_class_year.acronym)

        super(LearningClassEditForm, self).__init__(*args, **kwargs)

    def load_initial(self):
        self.fields['description'].initial = self.learning_class_year.description
        self.fields['description'].widget.attrs['class'] = "form-control"
        self.fields['used_by'].initial = self.used_by
        self.fields['used_by'].widget.attrs['disabled'] = False

    def save(self, commit=True):
        cleaned_data = self.cleaned_data
        self.link_management(cleaned_data.get('used_by'))
        self.update_description(cleaned_data.get('description'))

    def link_management(self, used_by):
        if used_by:
            self.create_link()
        else:
            self.delete_link()

    def create_link(self):
        a_learning_unit_component = mdl.learning_unit_component.search(self.learning_component_year,
                                                                       self.learning_unit_year).first()
        # Create a link between learning_class_year and learning_unit_component
        if a_learning_unit_component:
            links = mdl.learning_unit_component_class.search(a_learning_unit_component, self.learning_class_year)
            if not links.exists():
                new_learning_unit_component_class = mdl.learning_unit_component_class.LearningUnitComponentClass(
                    learning_class_year=self.learning_class_year,
                    learning_unit_component=a_learning_unit_component)
                new_learning_unit_component_class.save()

    def delete_link(self):
        a_learning_unit_component = mdl.learning_unit_component.search(self.learning_component_year,
                                                                       self.learning_unit_year).first()
        if a_learning_unit_component:
            # If exists delete link between learning_class_year and learning_unit_component
            links = mdl.learning_unit_component_class.search(a_learning_unit_component, self.learning_class_year)
            if links.exists():
                for l in links:
                    l.delete()

    def update_description(self, description):
        a_learning_class_year = mdl.learning_class_year.find_by_id(self.learning_class_year.id)
        a_learning_class_year.description = description
        a_learning_class_year.save()
