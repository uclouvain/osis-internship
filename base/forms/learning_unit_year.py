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

class LearningUnitYearForm(forms.Form):

    class Meta:
        model = learning_unit_year.LearningUnitYear
        exclude = ['external_id', 'changed', 'learning_unit', 'title']

    def clean_acronym(self):
        acronym = self.cleaned_data.get('acronym').upper()
        academic_year = self['academic_year'].value()

        print ("acronym: "+str(acronym))
        print ("academic_year: "+str(academic_year))

        if (str(academic_year) == "-1"):
            learning_unts=mdl.learning_unit_year.find_by_acronym(acronym)
            print(learning_unts)
            if not learning_unts:
                self.add_error('acronym', "If you dont specify an academic year, please enter a valid acronym.")
                return False
            else:
                #self.errors['academic_year'] = self.error_class()
                print (self.errors.as_data())
                print (self.is_valid())
                return True
