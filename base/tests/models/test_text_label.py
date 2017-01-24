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
from base.models import text_label


def create_text_label(entity_name, part_of, label, order, published):
    a_text_label = text_label.TextLabel(entity_name=entity_name, part_of=part_of, label=label, order=order,
                                        published=published)
    a_text_label.save()
    return a_text_label


class TextLabelTest(TestCase):

    def setUp(self):
        self.txtlabel1 = create_text_label(entity_name=1, part_of=None, label="WINDOW", order=30, published=1)
        self.txtlabel2 = create_text_label(entity_name=1, part_of=None, label="DOOR", order=5, published=1)
        self.txtlabel3 = create_text_label(entity_name=1, part_of=self.txtlabel1, label="SUBWINDOW01", order=10,
                                           published=1)
        self.txtlabel4 = create_text_label(entity_name=1, part_of=self.txtlabel1, label="SUBWINDOW01_A", order=5,
                                           published=1)

    def test_insert_new_text_label_same_order(self):
        self.order = 5
        self.part_of = self.txtlabel1
        foundtextlabel = text_label.TextLabel.objects.filter(part_of=self.part_of, order=self.order)
        self.assertEqual(foundtextlabel.count(), 1)

    def test_insert_new_text_label_children(self):
        foundparent = text_label.TextLabel.objects.filter(entity_name=self.txtlabel2.entity_name,
                                                          label=self.txtlabel2.label, order=self.txtlabel2.order)
        self.assertEqual(foundparent.count(), 1)


