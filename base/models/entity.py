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
import datetime
from base.models.entity_link import EntityLink


class Entity(models.Model):
    organization = models.ForeignKey('Organization', null=True)

    def _direct_children(self, date=None):
        if date is None:
            date = datetime.datetime.now()

        return EntityLink.objects.filter(parent=self,
                                         start_date__lte=date,
                                         end_date__gte=date
                                         )

    def get_direct_children(self, date=None):
        qs = self._direct_children(date).select_related("child")
        return [entity_link.child for entity_link in qs]

    def count_direct_children(self, date=None):
        return self._direct_children(date).count()
