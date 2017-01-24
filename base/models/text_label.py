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
from base.enums.entity_name import ENTITY_NAME
from base.models.exceptions import FunctionAgrumentMissingException

class TextLabelAdmin(admin.ModelAdmin):
    list_display = ('entity_name', 'part_of', 'label', 'order', 'published', 'children')
    fieldsets = ((None, {'fields': ('entity_name', 'part_of', 'label', 'order', 'published')}),)
    search_fields = ['acronym']


class TextLabel(models.Model):
    entity_name = models.IntegerField(choices=ENTITY_NAME)
    part_of = models.ForeignKey('self', blank=True, null=True)
    label = models.CharField(max_length=255)
    order = models.IntegerField(default=0)
    published = models.BooleanField()

    def save(self, *args, **kwargs):
        if self.order is None:
            raise AttributeError("Order must be defined.")
        super(TextLabel, self).save(*args, **kwargs)

    @property
    def children(self):
        return TextLabel.objects.filter(part_of=self.pk).order_by('order')

    def __str__(self):
        return self.label


def find_by_id(text_label_id):
    return TextLabel.objects.get(pk=text_label_id)


def find_by_ids(text_label_ids):
    return TextLabel.objects.filter(pk__in=text_label_ids)


def find_text_label_hierarchy(entity_id):
    txtlabel = TextLabel.objects.filter(entity_name=entity_id)
    list_labels = []
    for child_text_label in txtlabel:
        list_labels.append(child_text_label)
    return list_labels


def search(acronym=None):
    queryset = TextLabel.objects

    if acronym:
        queryset = queryset.filter(acronym=acronym)

    return queryset
