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
from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from dissertation.tests.models import test_proposition_dissertation, test_offer_proposition, test_adviser, \
    test_dissertation, test_faculty_adviser
from base.tests.models import test_student, test_offer_year, test_academic_year


class DissertationViewTestCase(TestCase):

    def setUp(self):
        self.client = Client()

        teacher = test_adviser.create_adviser_from_scratch(username='teacher', email='teacher@uclouvain.be',
                                                           password='teacher', type='PRF')
        manager = test_adviser.create_adviser_from_scratch(username='manager', email='manager@uclouvain.be',
                                                           password='manager', type='MGR')
        student = test_student.create_student(first_name="Prenometu", last_name="Nometu", registration_id="321654")

        academic_year = test_academic_year.create_academic_year()
        offer_year_start = test_offer_year.create_offer_year(acronym="test_offer",
                                                             title="test_offer",
                                                             academic_year=academic_year)
        offer = offer_year_start.offer
        offer_proposition = test_offer_proposition.create_offer_proposition(acronym="test_offer", offer=offer)
        test_faculty_adviser.create_faculty_adviser(manager, offer)

        # Create 5 propositions dissertations
        proposition_dissertations = []
        for x in range(0, 5):
            proposition_dissertation = test_proposition_dissertation.create_proposition_dissertation(
                title="Proposition " + str(x),
                adviser=teacher,
                person=teacher.person,
                offer_proposition=offer_proposition
            )
            proposition_dissertations.append(proposition_dissertation)

        # Create 5 dissertations with different roles ans status
        roles = ['PROMOTEUR', 'CO_PROMOTEUR', 'READER', 'PROMOTEUR', 'ACCOMPANIST']
        status = ['DRAFT', 'COM_SUBMIT', 'EVA_SUBMIT', 'TO_RECEIVE', 'DIR_SUBMIT']
        for x in range(0, 5):
            test_dissertation.create_dissertation(
                adviser=teacher,
                dissertation_role=roles[x],
                title="Dissertation " + str(x),
                author=student,
                status=status[x],
                offer_year_start=offer_year_start,
                proposition_dissertation=proposition_dissertations[x],
                active=True
                )

    def test_get_dissertations_list_for_teacher(self):
        self.client.login(username='teacher', password='teacher')
        url = reverse('dissertations_list')
        response = self.client.get(url)
        self.assertEqual(response.context[-1]['adviser_list_dissertations'].count(), 1)  # only 1 because 1st is DRAFT
        self.assertEqual(response.context[-1]['adviser_list_dissertations_copro'].count(), 1)
        self.assertEqual(response.context[-1]['adviser_list_dissertations_reader'].count(), 1)
        self.assertEqual(response.context[-1]['adviser_list_dissertations_accompanist'].count(), 1)

    def test_get_dissertations_list_for_manager(self):
        self.client.login(username='manager', password='manager')
        url = reverse('manager_dissertations_list')
        response = self.client.get(url)
        self.assertEqual(response.context[-1]['dissertations'].count(), 5)

    def test_search_dissertations_for_manager(self):
        self.client.login(username='manager', password='manager')
        url = reverse('manager_dissertations_search')

        response = self.client.get(url, data={"search": "no result search"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context[-1]['dissertations'].count(), 0)

        response = self.client.get(url, data={"search": "Dissertation 2"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context[-1]['dissertations'].count(), 1)

        response = self.client.get(url, data={"search": "Proposition 3"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context[-1]['dissertations'].count(), 1)

        response = self.client.get(url, data={"search": "Dissertation"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context[-1]['dissertations'].count(), 5)

        response = self.client.get(url, data={"search": "test_offer"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context[-1]['dissertations'].count(), 5)

        response = self.client.get(url, data={"search": "Nometu"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context[-1]['dissertations'].count(), 5)

        response = self.client.get(url, data={"search": "teacher"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context[-1]['dissertations'].count(), 5)
