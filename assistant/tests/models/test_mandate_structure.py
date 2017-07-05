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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django.test import TestCase
from assistant.tests.factories.assistant_mandate import AssistantMandateFactory
from assistant.tests.factories.mandate_structure import MandateStructureFactory
from base.tests.factories.structure import StructureFactory
from base.models.enums import structure_type
from assistant.models import mandate_structure


class TestMandateStructureFactory(TestCase):

    def setUp(self):
        self.assistant_mandate = AssistantMandateFactory()
        self.structure = StructureFactory(type=structure_type.FACULTY)
        self.mandate_structure = MandateStructureFactory(assistant_mandate=self.assistant_mandate,
                                                         structure=self.structure)

    def test_find_by_mandate_and_type(self):
        self.assertEqual(self.mandate_structure,
                         mandate_structure.find_by_mandate_and_type(self.assistant_mandate,
                                                                    structure_type.FACULTY).first())
