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

from django.db import models

from base.models.person import Person


class ProgrammeManager(models.Model):
    changed = models.DateTimeField(null=True)
    person  = models.ForeignKey('Person')
    faculty = models.ForeignKey('Structure')

    def __str__(self):
        return u"%s - %s" % (self.person, self.faculty)


def find_faculty_by_user(user):
    programme_manager = ProgrammeManager.objects.filter(person__user=user).first()
    if programme_manager:
        return programme_manager.faculty
    else:
        return None


def is_programme_manager(user, structure):
    person = Person.objects.get(user=user)
    if user:
        programme_manager = ProgrammeManager.objects.filter(person=person.id, faculty=structure)
        if programme_manager:
            return True
    return False