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
from base import models as mdl_base
from osis_common.models import message_template
import datetime
from django.contrib.auth.models import User


def create_user(username="foo", password="test"):
    user = User.objects.create_user(username=username, password=password, email="test@test.com")
    return user


def create_person(first_name, last_name):
    person = mdl_base.person.Person(first_name=first_name, last_name=last_name)
    person.save()
    return person


def create_student(first_name, last_name, registration_id):
    person = create_person(first_name, last_name)
    student = mdl_base.student.Student(person=person, registration_id=registration_id)
    student.save()
    return student


def create_tutor(first_name="Tutor", last_name="tutor"):
    person = create_person(first_name, last_name)
    tutor = mdl_base.tutor.Tutor(person=person)
    tutor.save()
    return tutor


def create_program_manager(offer_year):
    person = create_person("program", "manager")
    program_manager = mdl_base.program_manager.ProgramManager(person=person, offer_year=offer_year)
    program_manager.save()
    return program_manager


def create_attribution(tutor, learning_unit_year):
    attribution = mdl_base.attribution.Attribution(tutor=tutor, learning_unit_year=learning_unit_year)
    attribution.save()
    return attribution


