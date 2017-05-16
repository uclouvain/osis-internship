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
from cms.models import translated_text
from cms.enums import entity_name
from django.utils.safestring import mark_safe


class LearningUnitSpecificationsForm(forms.Form):
    learning_unit_year = language = None

    def __init__(self, learning_unit_year, iso, *args, **kwargs):
        self.learning_unit_year = learning_unit_year
        self.language = iso
        self.refresh_data()
        super(LearningUnitSpecificationsForm, self).__init__(*args, **kwargs)

    def refresh_data(self):
        texts_list = translated_text.search(entity=entity_name.LEARNING_UNIT_YEAR,
                                            reference=self.learning_unit_year.id,
                                            language=self.language)
        for trans_txt in texts_list:
            text_label = trans_txt.text_label.label
            setattr(self, text_label, mark_safe(trans_txt.text))