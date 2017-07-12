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


class LearningUnitComponentEditForm(forms.Form):
    planned_classes = forms.IntegerField(min_value=0, max_value=300)
    used_by = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        self.learning_unit_year = kwargs.pop('learning_unit_year', None)
        self.learning_component_year = kwargs.pop('learning_component_year', None)

        self.used_by = kwargs.pop('used_by', None)

        super(LearningUnitComponentEditForm, self).__init__(*args, **kwargs)

    def load_initial(self):
        self.fields['planned_classes'].initial = self.learning_component_year.planned_classes
        self.fields['used_by'].initial = self.used_by

    def save(self):
        cleaned_data = self.cleaned_data
        learning_component_yr = mdl.learning_component_year.find_by_id(self.learning_component_year.id)
        learning_component_yr.planned_classes = cleaned_data.get('planned_classes')
        learning_component_yr.save()
        self.link_management(cleaned_data.get('used_by'))

    def link_management(self, used_by):
        if used_by:
            self.create_link()
        else:
            self.delete_link()

    def create_link(self):
        # Create a link between learning_unit_year and learning_component_year
        links = mdl.learning_unit_component.search(self.learning_component_year, self.learning_unit_year)
        if not links.exists():
            new_learning_unit_component = mdl.learning_unit_component.LearningUnitComponent(
                learning_unit_year=self.learning_unit_year,
                learning_component_year=self.learning_component_year)
            new_learning_unit_component.save()

    def delete_link(self):
        # If exists delete link between learning_unit_year and learning_component_year
        links = mdl.learning_unit_component.search(self.learning_component_year, self.learning_unit_year)
        if links.exists():
            for l in links:
                l.delete()
