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
import random
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from base.models.person import Person
from dissertation.models.adviser import Adviser
from dissertation.tests.models import test_proposition_dissertation

from dissertation.models.proposition_dissertation import PropositionDissertation

class PropositionDissertationViewTestCase(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        #Teacher
        self.user_teacher = User.objects.create_user(username='teacher', email='teacher@uclouvain.be', password='teacher')
        self.person_teacher = Person.objects.create(user=self.user_teacher, first_name='teacher', last_name='teacher')
        self.adviser_teacher = Adviser.objects.create(person=self.person_teacher, type="PRF")
        #Manager
        self.user_manager = User.objects.create_user(username='manager', email='manager@uclouvain.be',
                                                     password='manager')
        self.person_manager = Person.objects.create(user=self.user_manager, first_name='manager', last_name='manager')
        self.adviser_manager = Adviser.objects.create(person=self.person_manager, type="MGR")
        #Proposition Dissertation
        self.proposition_dissertation = test_proposition_dissertation.create_proposition_dissertation\
            (title="First Proposition",advisor=self.adviser_teacher, person=self.person_teacher)
        self.proposition_dissertation_2 = test_proposition_dissertation.create_proposition_dissertation\
            (title="Second Proposition",advisor=self.adviser_teacher, person=self.person_teacher, max_number_student=10)

    ###########################
    #         TEACHER         #
    ###########################
    def test_get_new_proposition_dissertation(self):
        self.client.login(username=self.user_teacher.username, password='teacher')
        url = reverse('proposition_dissertation_new')
        response = self.client.get(url)
        self.assertEqual(response.context['form'].initial['active'], True)
        self.assertEqual(response.context['form'].initial['author'], self.adviser_teacher)

    def test_post_new_proposition_dissertation(self):
        self.client.login(username=self.user_teacher.username, password='teacher')
        url = reverse('proposition_dissertation_new')
        response = self.client.post(url, data=self.get_form_teacher_new_proposition_dissertation())
        # Nous pouvons tester uniquement la redirection, impossible de deviner l'ID
        self.assertEqual(response.status_code, 302)

    def test_get_detail_proposition_dissertation(self):
        self.client.login(username=self.user_teacher.username, password='teacher')
        url = reverse('proposition_dissertation_detail', args=[self.proposition_dissertation.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        context = response.context[-1]
        self.assertEqual(context.get("proposition_dissertation"), self.proposition_dissertation)

    def test_get_edit_proposition_dissertation(self):
        self.client.login(username=self.user_teacher.username, password='teacher')
        url = reverse('proposition_dissertation_edit', args=[self.proposition_dissertation.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        #Check form fields
        form = response.context['form']
        self.assertEqual(form.initial['title'], self.proposition_dissertation.title)
        self.assertEqual(form.initial['author'], self.proposition_dissertation.author.id)
        self.assertEqual(form.initial['collaboration'], self.proposition_dissertation.collaboration)
        self.assertEqual(form.initial['type'], self.proposition_dissertation.type)
        self.assertEqual(form.initial['level'], self.proposition_dissertation.level)
        self.assertEqual(form.initial['max_number_student'], self.proposition_dissertation.max_number_student)

    # Must correct bug osis/#1814
    # def test_get_wrong_edit_proposition_dissertation(self):
    #     self.client.login(username=self.user_teacher.username, password='teacher')
    #     url = reverse('proposition_dissertation_edit', args=[self.get_unused_id_proposition_dissertation()])
    #     response = self.client.get(url, follow=True)
    #     self.assertEqual(response.status_code, 404)

    def test_post_edit_proposition_dissertation(self):
        self.client.login(username=self.user_teacher.username, password='teacher')
        url = reverse('proposition_dissertation_edit', args=[self.proposition_dissertation.id])
        response = self.client.post(url, data = self.get_form_teacher_edit_proposition_dissertation())
        #Si l'objet est mis à jour redirection, impossible de tester actuellement le contenu
        self.assertEqual(response.status_code, 302)

    # def test_get_proposition_dissertations_created(self):
    #     self.client.login(username=self.user_teacher.username, password='teacher')
    #     all = PropositionDissertation.objects.all()
    #     url = reverse('proposition_dissertations')
    #     response = self.client.get(url)
    #     self.assertEqual(len(response.context['proposition_offers']), 2)

    def get_unused_id_proposition_dissertation(self):
        allowed_values = list(range(0, 600+1))
        allowed_values.remove(self.proposition_dissertation.id)
        allowed_values.remove(self.proposition_dissertation_2.id)
        return random.choice(allowed_values)

    def get_form_teacher_new_proposition_dissertation(self):
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

    def get_form_teacher_edit_proposition_dissertation(self):
        return {
            "title" : "Updated proposition dissertation",
            "visibility" : False,
            "author": self.adviser_teacher.id,
            "description" : "Updated proposition description",
            "type" : "OTH",
            "level" : "SPECIFIC",
            "collaboration" : "FORBIDDEN",
            "max_number_student" : 1
        }

    ###########################
    #         MANAGER         #
    ###########################