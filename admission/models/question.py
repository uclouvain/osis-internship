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
from django.utils.translation import ugettext_lazy as _


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('form', 'label', 'description', 'order')
    fieldsets = ((None, {'fields': ('label', 'description', 'type', 'order', 'required', 'form')}),)


QUESTION_TYPES = (
    ('SHORT_INPUT_TEXT', _('Short input text')),
    ('LONG_INPUT_TEXT', _('Long input text')),
    ('RADIO_BUTTON', _('Radio button')),
    ('CHECKBOX', _('Checkbox')),
    ('DROPDOWN_LIST', _('Dropdown list')),
    ('UPLOAD_BUTTON', _('Upload button')),
    ('DOWNLOAD_LINK', _('Download link')),
    ('HTTP_LINK', _('HTTP link'))
)


class Question(models.Model):

    form = models.ForeignKey('Form')
    label = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    order = models.IntegerField(blank=True, null=True)
    required = models.BooleanField(default=False)

    def __str__(self):
        return u"%s" % self.label


def find_by_offer_form(offer_form):
    return Question.objects.filter(form=offer_form) \
                           .order_by('label', 'description')


def find_by_id(question_id):
    return Question.objects.get(pk=question_id)
