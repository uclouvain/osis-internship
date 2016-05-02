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
from django.utils import timezone


class MessageHistory(models.Model):
    template = models.ForeignKey('MessageTemplate')
    subject = models.CharField(max_length=255)
    content = models.TextField()
    origin = models.EmailField()
    destination = models.EmailField()
    created = models.DateTimeField(editable=False)
    sent_by_mail_date = models.DateTimeField(null=True)
    sent_to_myosis_date = models.DateTimeField(null=True)

    def __str__(self):
        return self.subject

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
        return super(MessageHistory, self).save(*args, **kwargs)


def find_by_reference(reference):
    messages_history = MessageHistory.objects.filter(template__reference=reference)
    return messages_history


def find_by_reference_and_language(reference,language):
    messages_history = MessageHistory.objects.filter(template__reference=reference, template__language=language)
    return messages_history