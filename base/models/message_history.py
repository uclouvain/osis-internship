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
from django.db.models import Q
from django.utils import timezone


class MessageHistory(models.Model):
    subject = models.CharField(max_length=255)
    content_txt = models.TextField()
    content_html = models.TextField()
    person = models.ForeignKey('Person')
    created = models.DateTimeField(editable=False)
    sent = models.DateTimeField(null=True)
    reference = models.CharField(max_length=100, null=True, db_index=True)
    show_in_myosis = models.BooleanField(default=True)
    read_in_myosis = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
        return super(MessageHistory, self).save(*args, **kwargs)

    def __str__(self):
        return self.subject


def find_by_id(message_history_id):
    message_history = MessageHistory.objects.get(id=message_history_id)
    return message_history


def search(limit=100, **kwargs):
    if not kwargs:
        messages_history = MessageHistory.objects.all().order_by('created')[:limit]
    else:
        queryset = MessageHistory.objects
        if kwargs.get('reference'):
            queryset = queryset.filter(reference__icontains=kwargs.get('reference'))
        if kwargs.get('subject'):
            queryset = queryset.filter(subject__icontains=kwargs.get('subject'))
        if kwargs.get('recipient'):
            queryset = queryset.filter(Q(person__email__icontains=kwargs.get('recipient')) |
                                       Q(person__last_name__icontains=kwargs.get('recipient')) |
                                       Q(person__user__username__icontains=kwargs.get('recipient')))
        if kwargs.get('not_sent'):
            queryset = queryset.filter(sent__isnull=True)

        queryset = queryset.order_by('created')
        messages_history = queryset[:limit]
    return messages_history


def find_my_messages(username):
    return MessageHistory.objects.filter(person__user__username=username).filter(show_in_myosis=True).order_by('sent')


def delete_my_message(message_id):
    MessageHistory.objects.filter(id=message_id).update(show_in_myosis=False)