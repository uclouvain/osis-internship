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
from django.test import TestCase
from base.tests.models import test_student
from internship.tests.models import test_organization, test_internship_speciality, test_internship_choice, \
    test_internship_offer, test_period, test_period_internship_places
from internship.views import affectation_statistics_beta


class TestAffectationGeneration(TestCase):
    def setUp(self):
        self.student_1 = test_student.create_student("Student1", "Last", "1")
        self.student_2 = test_student.create_student("Student2", "Last", "2")
        self.student_3 = test_student.create_student("Student3", "Last", "3")
        self.student_4 = test_student.create_student("Student4", "Last", "4")

        organization_1 = test_organization.create_organization(name="organization1", reference="01")
        organization_2 = test_organization.create_organization(name="organization2", reference="02")
        organization_3 = test_organization.create_organization(name="organization3", reference="03")

        speciality_1 = test_internship_speciality.create_speciality(name="spec1")
        speciality_2 = test_internship_speciality.create_speciality(name="spec2")
        speciality_3 = test_internship_speciality.create_speciality(name="spec3")

        choice_1 = test_internship_choice.create_internship_choice(organization_1, self.student_1, speciality_1,
                                                                   internship_choice=1)
        choice_2 = test_internship_choice.create_internship_choice(organization_1, self.student_1, speciality_2,
                                                                   internship_choice=2)
        choice_3 = test_internship_choice.create_internship_choice(organization_2, self.student_2, speciality_3,
                                                                   internship_choice=1)
        choice_4 = test_internship_choice.create_internship_choice(organization_3, self.student_2, speciality_2,
                                                                   internship_choice=2)
        choice_5 = test_internship_choice.create_internship_choice(organization_1, self.student_3, speciality_1,
                                                                   internship_choice=1)
        choice_6 = test_internship_choice.create_internship_choice(organization_2, self.student_4, speciality_1,
                                                                   internship_choice=1)
        choice_7 = test_internship_choice.create_internship_choice(organization_2, self.student_4, speciality_3,
                                                                   internship_choice=2)
        choice_8 = test_internship_choice.create_internship_choice(organization_3, self.student_4, speciality_2,
                                                                   internship_choice=3)

        offer_1 = test_internship_offer.create_specific_internship_offer(organization_1, speciality_1)
        offer_2 = test_internship_offer.create_specific_internship_offer(organization_1, speciality_2)
        offer_3 = test_internship_offer.create_specific_internship_offer(organization_2, speciality_1)
        offer_4 = test_internship_offer.create_specific_internship_offer(organization_2, speciality_3)
        offer_5 = test_internship_offer.create_specific_internship_offer(organization_3, speciality_2)

        period_9 = test_period.create_period("P9")
        period_10 = test_period.create_period("P10")
        period_11 = test_period.create_period("P11")
        period_12 = test_period.create_period("P12")

        test_period_internship_places.create_period_places(offer_1, period_9)
        test_period_internship_places.create_period_places(offer_1, period_11)
        test_period_internship_places.create_period_places(offer_2, period_10)
        test_period_internship_places.create_period_places(offer_3, period_12)
        test_period_internship_places.create_period_places(offer_4, period_9)
        test_period_internship_places.create_period_places(offer_4, period_10)
        test_period_internship_places.create_period_places(offer_5, period_11)
        test_period_internship_places.create_period_places(offer_5, period_12)

    def test_init_solver(self):
        solver = affectation_statistics_beta.init_solver()
        self.assertEqual(solver.get_number_students(), 4)
        self.assertEqual(solver.get_number_offers(), 5)

        try:
            affectation_statistics_beta.launch_solver(solver)
        except Exception:
            self.fail()
