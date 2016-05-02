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
    template = models.ForeignKey('MessageTemplate')
    subject = models.CharField(max_length=255)
    content = models.TextField()
    origin = models.EmailField()
    person = models.ForeignKey('Person')
    created = models.DateTimeField(editable=False)
    sent_by_mail_date = models.DateTimeField(null=True)
    sent_to_myosis_date = models.DateTimeField(null=True)

    def __str__(self):
        return self.subject

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
        return super(MessageHistory, self).save(*args, **kwargs)


def find_by_id(message_history_id):
    message_history = MessageHistory.objects.get(id=message_history_id)
    return message_history


def find(limit=100, **kwargs):
    if not kwargs:
        messages_history = MessageHistory.objects.all().order_by('created')[:limit]
    else:
        queryset = MessageHistory.objects
        if 'reference' in kwargs and kwargs['reference']:
            queryset = queryset.filter(template__reference__icontains=kwargs['reference'])
        if 'language' in kwargs and kwargs['language']:
            queryset = queryset.filter(template__language=kwargs['language'])
        if 'subject' in kwargs and kwargs['subject']:
            queryset = queryset.filter(subject__icontains=kwargs['subject'])
        if 'origin' in kwargs and kwargs['origin']:
            queryset = queryset.filter(origin__icontains=kwargs['origin'])
        if 'recipient' in kwargs and kwargs['recipient']:
            queryset = queryset.filter(Q(person__email__icontains=kwargs['recipient']) |
                                       Q(person__last_name__icontains=kwargs['recipient']) |
                                       Q(person__user__username__icontains=kwargs['recipient']))
        if 'sent_by_mail' in kwargs and kwargs['sent_by_mail']:
            queryset = queryset.exclude(sent_by_mail_date__isnull=True)
        if 'sent_to_myosis' in kwargs and kwargs['sent_to_myosis']:
            queryset = queryset.exclude(sent_to_myosis_date__isnull=True)
        if 'orber_by' in kwargs and kwargs['order_by']:
            queryset = queryset.order_by(kwargs['order_by'])
        else:
            queryset = queryset.order_by('created')
        messages_history = queryset[:limit]
    return messages_history
