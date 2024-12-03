##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2021 Université catholique de Louvain (http://www.uclouvain.be)
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
import uuid as uuid

from django.contrib.admin import ModelAdmin
from django.db import models
from django.db.models import JSONField
from django.utils.translation import gettext_lazy as _
from ordered_model.models import OrderedModel

from internship.models.enums.response_type import ResponseType


class PlaceEvaluationItemAdmin(ModelAdmin):
    list_display = ("order", "statement", "type", "cohort")
    list_filter = ("type", "cohort")
    search_fields = ["statement"]
    ordering = ("cohort", "order")


class PlaceEvaluationItem(OrderedModel):

    uuid = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, db_index=True
    )

    cohort = models.ForeignKey('internship.Cohort', on_delete=models.CASCADE, null=True, verbose_name=_("Cohort"))
    statement = models.CharField(max_length=300, verbose_name=_("Statement"))
    type = models.CharField(
        choices=ResponseType.choices(), default=ResponseType.OPEN.value, max_length=10, verbose_name=_("Type")
    )
    options = JSONField(default=list, verbose_name=_("Options"))

    active = models.BooleanField(default=True, verbose_name=_("Active"))
    required = models.BooleanField(default=True, verbose_name=_("Required"))

    order_with_respect_to = 'cohort'

    def __str__(self):
        return f'({self.order}) {self.statement}'
