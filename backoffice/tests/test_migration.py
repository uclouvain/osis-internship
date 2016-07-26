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

# This class tests the portal_migration functions.


from django.test import TestCase
from base.models import student, tutor, person, domain
from reference.models import country
from django.contrib.auth.models import User
import backoffice.portal_migration as portal_migration
import random


class PortalMigrationTest(TestCase):
    def setUp(self):
        PortalMigrationTest.createStudents()

    def testGetModelClass(self):
        list_expected = ['reference.Country',
                         'admission.Domain',
                         'base.Student',
                         'base.Tutor']
        list_actual = [portal_migration.get_model_class_str(country.Country),
                       portal_migration.get_model_class_str(domain.Domain),
                       portal_migration.get_model_class_str(student.Student),
                       portal_migration.get_model_class_str(tutor.Tutor)]
        self.assertListEqual(list_expected, list_actual, "get_model_class_str doesn't "
                                                         "return the correct string for"
                                                         "the class")

    @staticmethod
    def createStudents():
        list_first_names = ['Henry', 'Pierre', 'Alexandre', 'Jeanne', 'Suzanne', 'Olivier',
                            'Jean', 'Lisa']
        list_last_names = ['Smith', 'Brown', 'Lopez', 'Lewis', 'Robinson', 'Diaz',
                           'Kelly', 'Howard']
        list_password = ['qwerty', 'mustang', 'master', 'superman', 'ranger', '1234', 'trustno1',
                         'tigger']
        list_global_ids = PortalMigrationTest.generateListIds(number_of_id=8, length_of_id=8)

        list_users = PortalMigrationTest.createUsers(list_last_names, list_password)
        list_persons = PortalMigrationTest.createPersons(list_users, list_global_ids, list_first_names,
                                                         list_last_names)
        for i in range(0, len(list_last_names)):
            a_student = student.Student(person=list_persons[i],
                                        registration_id=list_global_ids[i])
            a_student.save()


    @staticmethod
    def createUsers(list_usernames, list_passwords):
        """
        Return a list of users having as usernames and passwords the one in the list.
        The two list must have the same length.
        :param self:
        :param list_usernames: a list of usernames
        :param list_passwords: a lsit of passwords
        :return: A list of users.
        """
        list_users = []

        for i in range(0, len(list_usernames)):
            a_user = User.objects.create_user(list_usernames[i],
                                              password=list_passwords[i])
            list_users.append(a_user)

        return list_users

    @staticmethod
    def createPersons(list_users, list_global_id, list_first_names, list_last_names):
        """
        Return a list of persons.
        The lists must have the same length.
        :param list_users: a list of user objects
        :param list_global_id: a list of global ids
        :param list_first_names: a list of first names
        :param list_last_names: a list of last names
        :return: A list of persons
        """
        list_persons = []

        for i in range(0, len(list_users)):
            email = list_first_names[i] + list_last_names[i] + "@test.com"
            a_person = person.Person(user=list_users[i],
                                     global_id=list_global_id[i],
                                     first_name=list_first_names[i],
                                     last_name=list_last_names[i],
                                     email=email)
            a_person.save()
            list_persons.append(a_person)

        return list_persons

    @staticmethod
    def generateListIds(number_of_id, length_of_id):
        """
        Generate a list of ids.
        :param number_of_id: The number of ids to be generated
        :param length_of_id: The number of characters of the ids.
        :return: A list.
        """
        list_ids = []

        for i in range(0, number_of_id):
            a_id =  PortalMigrationTest.generateId(length_of_id)
            list_ids.append(a_id)

        return list_ids

    @staticmethod
    def generateId(length):
        """
        Generate a id  of length "length". An id is comprised only of numerical characters.
        :param length: The number of characters of the id.
        :return: A string.
        """
        str_id = ""

        for i in range(0, length):
            str_id += str(random.randint(0, 9))

        return str_id
