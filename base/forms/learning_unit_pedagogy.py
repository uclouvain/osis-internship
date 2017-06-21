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
from ckeditor.widgets import CKEditorWidget
from cms.enums import entity_name
from cms.models import translated_text


class LearningUnitPedagogyForm(forms.Form):
    learning_unit_year = language = None
    resume = forms.CharField(widget=CKEditorWidget(config_name='minimal'), required=False)
    bibliography = forms.CharField(widget=CKEditorWidget(config_name='minimal'), required=False)
    teaching_methods = forms.CharField(widget=CKEditorWidget(config_name='minimal'), required=False)
    evaluation_methods = forms.CharField(widget=CKEditorWidget(config_name='minimal'), required=False)
    other_informations = forms.CharField(widget=CKEditorWidget(config_name='minimal'), required=False)
    online_resources = forms.CharField(widget=CKEditorWidget(config_name='minimal'), required=False)

    def __init__(self, *args, **kwargs):
        self.learning_unit_year = kwargs.pop('learning_unit_year', None)
        self.language = kwargs.pop('language', None)
        self.prefix = self.language[0] # FORM Prefix is the ISO code
        super(LearningUnitPedagogyForm, self).__init__(*args, **kwargs)
        self.load_initial()

    def load_initial(self):
        translated_texts_list = self._get_all_translated_text_related()

        for trans_txt in translated_texts_list:
            text_label = trans_txt.text_label.label
            self.fields[text_label].initial = trans_txt.text

    def save(self):
        translated_texts_list = self._get_all_translated_text_related()
        cleaned_data = self.cleaned_data

        # Update
        for trans_txt in translated_texts_list:
            text_label = trans_txt.text_label.label
            trans_txt.text = cleaned_data.pop(text_label, None)
            trans_txt.save()

    def _get_all_translated_text_related(self):
        language_iso = self.language[0]
        text_labels_name = ['resume', 'bibliography', 'teaching_methods', 'evaluation_methods',
                            'other_informations', 'online_resources']
        return translated_text.search(entity=entity_name.LEARNING_UNIT_YEAR,
                                      reference=self.learning_unit_year.id,
                                      language=language_iso,
                                      text_labels_name=text_labels_name)