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
from django.contrib import admin
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


class Message(models.Model):
    TYPE = (
        ('TO_ALL_ASSISTANTS', _('To_all_assistants')),
        ('TO_ALL_DEANS', _('To_All_Deans')),
        ('TO_PHD_SUPERVISOR', _('To_Phd_Supervisor')),
        ('TO_ONE_DEAN', _('To_One_Dean'))
    )
    sender = models.ForeignKey('assistant.Manager')
    academic_year = models.ForeignKey('base.AcademicYear')
    date = models.DateTimeField(default=timezone.now, null=True)
    type = models.CharField(max_length=20, choices=TYPE)
    
    def __str__(self):
        return u"%s (%s : %s)" % self.sender.person, self.type, self.date
