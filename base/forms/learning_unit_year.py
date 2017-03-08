##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2016 Université catholique de Louvain (http://www.uclouvain.be)
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
from base.models import learning_unit_year
from base import models as mdl
from django.utils.translation import ugettext as trans

class LearningUnitYearForm(forms.ModelForm):

    class Meta:
        model = learning_unit_year.LearningUnitYear
        exclude = ['external_id', 'changed']

    def clean(self):
        cleaned_data = super(LearningUnitYearForm, self).clean()
        print (cleaned_data)

    def clean_acronym(self):
        print ("hello")
        acronym = self.cleaned_data.get('acronym')

        print ("acronym: "+str(acronym))

        learning_unts=mdl.learning_unit_year.find_by_acronym(acronym)
        if learning_unts is None:
            #self._errors['acronym'] = trans("If you dont specify an academic year, please enter a valid acronym.")
            #self.add_error('acronym', forms.ValidationError(_('file_must_be_xlsx'), code='invalid'))
            self.add_error('acronym', "If you dont specify an academic year, please enter a valid acronym.")
            print (self.errors.as_data())
            return False