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
from django.test import TestCase, RequestFactory, Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from base.models.person import Person
from dissertation.models.adviser import Adviser

class PropositionDissertationNewViewTestCase(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.user_teacher = User.objects.create_user(username='teacher', email='teacher@uclouvain.be', password='teacher')
        self.person_teacher = Person.objects.create(user=self.user_teacher, first_name='teacher', last_name='teacher')
        self.adviser_teacher = Adviser.objects.create(person=self.person_teacher, type="PRF")
        self.user_manager = User.objects.create_user(username='manager', email='manager@uclouvain.be',
                                                     password='manager')
        self.person_manager = Person.objects.create(user=self.user_manager, first_name='manager', last_name='manager')
        self.adviser_manager = Adviser.objects.create(person=self.person_manager, type="MGR")

    def test_get_new_proposition_dissertation(self):
        self.client.login(username=self.user_teacher.username, password='teacher')
        url = reverse('proposition_dissertation_new')
        response = self.client.get(url)
        self.assertEqual(response.context['form'].initial['visibility'], True)
        self.assertEqual(response.context['form'].initial['author'], self.adviser_teacher)

    def test_post_new_proposition_dissertation(self):
        self.client.login(username=self.user_teacher.username, password='teacher')
        url = reverse('proposition_dissertation_new')
        response = self.client.post(url, data=self.get_form_teacher_with_all_attributes_filled())
        # Nous pouvons tester uniquement la redirection, impossible de deviner l'ID
        self.assertEqual(response.status_code, 302)






    def get_form_teacher_with_all_attributes_filled(self):
        return {
            "title": "proposition_dissertation",
            "visibility": True,
            "author": self.adviser_teacher.id,
            "description": "proposition dissertation description",
            "type": "OTH",
            "level": "SPECIFIC",
            "collaboration": "FORBIDDEN",
            "max_number_student": 5
        }