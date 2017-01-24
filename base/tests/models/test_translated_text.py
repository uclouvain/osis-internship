##############################################################################
#
# OSIS stands for Open Student Information System. It's an application
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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django.test import TestCase
from base.models import translated_text
from base.models import text_label
from reference.models.language import Language
from base.models.exceptions import FunctionTxtLabelExitsException


def create_translated_text(entity_name, reference, language, txtlabel, text):
    a_translated_text = translated_text.TranslatedText(entity_name=entity_name, reference=reference, language=language,
                                                       text_label=txtlabel, text=text)
    a_translated_text.save(functions=[])
    return a_translated_text


class TranslatedTextTest(TestCase):

    def setUp(self):
        self.parent = text_label.TextLabel(entity_name="1", part_of=None, label="WINDOW", order=30,
                                           published=1)
        self.languagefr = Language.objects.create(code="FR", name="Francais")

    def test_insert_new_translated_text(self):
        txtlabel1 = text_label.TextLabel(entity_name=1, part_of=None, label="KEYBOARD", order=80, published=1)
        wrong_translatedtxt = translated_text.TranslatedText(entity_name=1,  reference=self.parent,
                                                             language=self.languagefr, text_label=txtlabel1,
                                                             text="1545454")
        self.assertRaises(FunctionTxtLabelExitsException, wrong_translatedtxt.save, functions=[])
