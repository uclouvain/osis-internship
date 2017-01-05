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
from base.models import learning_unit_year
from base.tests.models import test_learning_unit, test_tutor, test_academic_year
from attribution.tests.models import test_attribution


def create_learning_unit_year(acronym, title, academic_year):
    a_learning_unit_year = \
        learning_unit_year.LearningUnitYear(acronym=acronym, title=title,
                                            academic_year=academic_year,
                                            learning_unit=test_learning_unit.create_learning_unit(acronym, title))
    a_learning_unit_year.save()
    return a_learning_unit_year


class LearningUnitYearTest(TestCase):

    def setUp(self):
        self.tutor = test_tutor.create_tutor(first_name="Laura", last_name="Dupont")
        self.academic_year = test_academic_year.create_academic_year()
        self.learning_unit_year = create_learning_unit_year("LDROI1004", "Juridic law courses", self.academic_year)
        self.attribution = test_attribution.create_attribution(self.tutor, self.learning_unit_year)

    def test_find_by_tutor_with_none_argument(self):
        self.assertEquals(learning_unit_year.find_by_tutor(None), None)

    def test_find_by_tutor(self):
        learning_unit_years = learning_unit_year.find_by_tutor(self.tutor)
        self.assertEquals(len(learning_unit_years), 1)
        self.assertEquals(learning_unit_years[0].acronym, "LDROI1004")
