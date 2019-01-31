# ##################################################################################################
#  OSIS stands for Open Student Information System. It's an application                            #
#  designed to manage the core business of higher education institutions,                          #
#  such as universities, faculties, institutes and professional schools.                           #
#  The core business involves the administration of students, teachers,                            #
#  courses, programs and so on.                                                                    #
#                                                                                                  #
#  Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)              #
#                                                                                                  #
#  This program is free software: you can redistribute it and/or modify                            #
#  it under the terms of the GNU General Public License as published by                            #
#  the Free Software Foundation, either version 3 of the License, or                               #
#  (at your option) any later version.                                                             #
#                                                                                                  #
#  This program is distributed in the hope that it will be useful,                                 #
#  but WITHOUT ANY WARRANTY; without even the implied warranty of                                  #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                                   #
#  GNU General Public License for more details.                                                    #
#                                                                                                  #
#  A copy of this license - GNU General Public License - is available                              #
#  at the root of the source code of this program.  If not,                                        #
#  see http://www.gnu.org/licenses/.                                                               #
# ##################################################################################################
from django.core.management.sql import emit_post_migrate_signal

from base.models.person import Person
from internship.models.internship_student_information import InternshipStudentInformation


def add_init_internship_manager_group(apps, schema_editor):
    # create group
    db_alias = schema_editor.connection.alias
    emit_post_migrate_signal(2, False, db_alias)
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    internship_manager_group, created = Group.objects.get_or_create(name='internship_manager')
    if created:
        # Add permissions to group
        student_path_perm = Permission.objects.get(codename='can_access_student_path')
        internships_perm = Permission.objects.get(codename='can_access_internship')
        internship_manager_perm = Permission.objects.get(codename='is_internship_manager')
        internship_manager_group.permissions.add(student_path_perm, internships_perm, internship_manager_perm)


def linkToDefaultCohort(apps, schema_editor):
    Cohort = apps.get_model("internship", "Cohort")
    InternshipOffer = apps.get_model("internship", "InternshipOffer")
    db_alias = schema_editor.connection.alias
    default_cohort = Cohort.objects.first()
    InternshipOffer.objects.all().update(cohort=default_cohort)


def cleanupStudentInternshipsAndPersons(apps, schema_editor):
    bad_student_infos = InternshipStudentInformation.objects.filter(cohort_id=2)
    bad_person_ids = bad_student_infos.values_list("person_id", flat=True)
    Person.objects.filter(id__in=bad_person_ids).delete()
    bad_student_infos.delete()
