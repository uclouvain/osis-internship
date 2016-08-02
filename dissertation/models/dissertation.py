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
from django.contrib import admin
from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from base.models import offer_year, student, academic_year
from . import proposition_dissertation
from . import offer_proposition


class DissertationAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'active')


STATUS_CHOICES = (
    ('DRAFT', _('draft')),
    ('DIR_SUBMIT', _('submitted_to_director')),
    ('DIR_OK', _('accepted_by_director')),
    ('DIR_KO', _('refused_by_director')),
    ('COM_SUBMIT', _('submitted_to_commission')),
    ('COM_OK', _('accepted_by_commission')),
    ('COM_KO', _('refused_by_commission')),
    ('EVA_SUBMIT', _('submitted_to_first_year_evaluation')),
    ('EVA_OK', _('accepted_by_first_year_evaluation')),
    ('EVA_KO', _('refused_by_first_year_evaluation')),
    ('TO_RECEIVE', _('to_be_received')),
    ('TO_DEFEND', _('to_be_defended')),
    ('DEFENDED', _('defended')),
    ('ENDED', _('ended')),
    ('ENDED_WIN', _('ended_win')),
    ('ENDED_LOS', _('ended_los')),
)


class Dissertation(models.Model):

    DEFEND_PERIODE_CHOICES = (
        ('UNDEFINED', _('undefined')),
        ('JANUARY', _('january')),
        ('JUNE', _('june')),
        ('SEPTEMBER', _('september')),
    )

    title = models.CharField(max_length=200)
    author = models.ForeignKey(student.Student)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='DRAFT')
    defend_periode = models.CharField(max_length=12, choices=DEFEND_PERIODE_CHOICES, default='UNDEFINED')
    defend_year = models.ForeignKey(academic_year.AcademicYear, blank=True, null=True)
    offer_year_start = models.ForeignKey(offer_year.OfferYear)
    proposition_dissertation = models.ForeignKey(proposition_dissertation.PropositionDissertation)
    description = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=True)
    creation_date = models.DateTimeField(auto_now_add=True, editable=False)
    modification_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def deactivate(self):
        self.active = False
        self.save()

    def set_status(self, status):
        self.status = status
        self.save()

    def go_forward(self):
        if self.status == 'DRAFT' or self.status == 'DIR_KO':
            self.set_status('DIR_SUBMIT')

        elif self.status == 'TO_RECEIVE':
            self.set_status('TO_DEFEND')

        elif self.status == 'TO_DEFEND':
            self.set_status('DEFENDED')

    def accept(self):
        offer_prop = offer_proposition.search_by_offer(self.offer_year_start.offer)
        if offer_prop.validation_commission_exists and self.status == 'DIR_SUBMIT':
            self.set_status('COM_SUBMIT')

        elif offer_prop.evaluation_first_year and (self.status == 'DIR_SUBMIT' or self.status == 'COM_SUBMIT'):
            self.set_status('EVA_SUBMIT')

        elif self.status == 'EVA_SUBMIT':
            self.set_status('TO_RECEIVE')

        elif self.status == 'DEFENDED':
            self.set_status('ENDED_WIN')

        else:
            self.set_status('TO_RECEIVE')

    def refuse(self):
        if self.status == 'DIR_SUBMIT':
            self.set_status('DIR_KO')

        elif self.status == 'COM_SUBMIT':
            self.set_status('COM_KO')

        elif self.status == 'EVA_SUBMIT':
            self.set_status('EVA_KO')

        elif self.status == 'DEFENDED':
            self.set_status('ENDED_LOS')

    class Meta:
        ordering = ["author__person__last_name", "author__person__middle_name", "author__person__first_name", "title"]


def search(terms=None, active=True):
    queryset = Dissertation.objects.all()
    if terms:
        queryset = queryset.filter(
            Q(author__person__first_name__icontains=terms) |
            Q(author__person__middle_name__icontains=terms) |
            Q(author__person__last_name__icontains=terms) |
            Q(description__icontains=terms) |
            Q(proposition_dissertation__title__icontains=terms) |
            Q(proposition_dissertation__author__person__first_name__icontains=terms) |
            Q(proposition_dissertation__author__person__middle_name__icontains=terms) |
            Q(proposition_dissertation__author__person__last_name__icontains=terms) |
            Q(status__icontains=terms) |
            Q(title__icontains=terms)
        ).filter(active=active).distinct()
    return queryset


def search_by_proposition_author(terms=None, active=True, proposition_author=None):
    return search(terms=terms, active=active).filter(proposition_dissertation__author=proposition_author)


def search_by_offer(offer):
    return Dissertation.objects.filter(offer_year_start__offer=offer)
