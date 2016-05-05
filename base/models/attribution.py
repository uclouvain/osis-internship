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


class AttributionAdmin(admin.ModelAdmin):
    list_display = ('tutor','function','learning_unit','start_date', 'end_date', 'changed')
    list_filter = ('function',)
    fieldsets = ((None, {'fields': ('learning_unit','tutor','function','start_date','end_date')}),)
    raw_id_fields = ('learning_unit', 'tutor' )
    search_fields = ['tutor__person__first_name', 'tutor__person__last_name', 'learning_unit__acronym']


class Attribution(models.Model):
    FUNCTION_CHOICES = (
        ('COORDINATOR', 'Coordinator'),
        ('PROFESSOR', 'Professor'))

    external_id = models.CharField(max_length=100, blank=True, null=True)
    changed = models.DateTimeField(null=True)
    start_date = models.DateField(auto_now=False, blank=True, null=True, auto_now_add=False)
    end_date = models.DateField(auto_now=False, blank=True, null=True, auto_now_add=False)
    function = models.CharField(max_length=15, blank=True, null=True, choices=FUNCTION_CHOICES, db_index=True)
    learning_unit = models.ForeignKey('LearningUnit')
    tutor = models.ForeignKey('Tutor')

    def __str__(self):
        return u"%s - %s" % (self.tutor.person, self.function)


def find_by_tutor(a_tutor):
    attributions = Attribution.objects.filter(tutor=a_tutor)
    return attributions


def get_assigned_tutor(user):
    attribution = Attribution.objects.filter(tutor__person__user=user).first()
    if attribution:
        return attribution.tutor
    else:
        return None


def find_by_learning_unit(a_learning_unit):
    attributions = Attribution.objects.filter(learning_unit=a_learning_unit) \
                              .order_by('tutor__person__last_name', 'tutor__person__first_name')
    return attributions


def find_by_function(tutor, a_learning_unit, function):
    attributions_coord = Attribution.objects.filter(learning_unit=a_learning_unit) \
                                     .filter(tutor=tutor.id)\
                                     .filter(function=function)
    if attributions_coord:
        return True
    return False


def find_by_learning_unit_year_ids(learning_unit_year_ids, function=None):
    """
    :param learning_unit_year_ids: Ids from which to find attributions.
    :param function: Filter the resulset by Attribution.function
    :return: Find all attributions for the learningUnitYears in parameter.
    """
    queryset = Attribution.objects
    if function:
        queryset = queryset.filter(function=function)
    queryset = queryset.filter(learning_unit_id__in=learning_unit_year_ids)
    return queryset
