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
from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver
from base.models.program_manager import ProgramManager
from base.models.student import Student
from base.models.tutor import Tutor
import base.models as mdl_base
import backoffice.portal_migration as portal_migration

queue_name = 'osis_base'


@receiver(post_save, sender=Tutor)
def add_to_tutors_group(sender, instance, **kwargs):
    if kwargs.get('created', True) :
        # Send new tutor to osis-portal
        records = {"tutors": mdl_base.tutor.serialize_list_tutors([instance]),
                   "persons": mdl_base.person.serialize_list_persons([instance.person])}
        portal_migration.migrate_records(records=records, model_class=instance.__class__,
                                         queue_name=queue_name)
        if instance.person.user:
            tutors_group = Group.objects.get(name='tutors')
            instance.person.user.groups.add(tutors_group)


@receiver(post_save, sender=Student)
def add_to_students_group(sender, instance, **kwargs):
    if kwargs.get('created', True):
        # Send new student to osis-portal
        records = {"students": mdl_base.student.serialize_list_students([instance]),
                   "persons": mdl_base.person.serialize_list_persons([instance.person])}
        portal_migration.migrate_records(records=records, model_class=instance.__class__,
                                         queue_name=queue_name)
        if instance.person.user:
            students_group = Group.objects.get(name='students')
            instance.person.user.groups.add(students_group)


@receiver(post_save, sender=ProgramManager)
def add_to_pgm_managers_group(sender, instance, **kwargs):
    if kwargs.get('created', True) and instance.person.user:
        pgm_managers_group = Group.objects.get(name='program_managers')
        instance.person.user.groups.add(pgm_managers_group)
