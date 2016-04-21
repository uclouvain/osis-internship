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
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.contrib import admin
from base.models import person, attribution, academic_year, program_manager, session_exam, exam_enrollment


class TutorAdmin(admin.ModelAdmin):
    list_display = ('person', 'changed')
    fieldsets = ((None, {'fields': ('person',)}),)
    raw_id_fields = ('person', )
    search_fields = ['person__first_name', 'person__last_name']


class Tutor(models.Model):
    external_id = models.CharField(max_length=100, blank=True, null=True)
    changed = models.DateTimeField(null=True)
    person = models.OneToOneField('Person')

    def __str__(self):
        return u"%s" % self.person


def find_by_user(user):
    try:
        pers = person.find_by_user(user)
        tutor = Tutor.objects.get(person=pers)
        return tutor
    except ObjectDoesNotExist:
        return None


def find_by_person(a_person):
    try:
        tutor = Tutor.objects.get(person=a_person)
        return tutor
    except ObjectDoesNotExist:
        return None


def find_by_learning_unit(a_learning_unit):
    tutor_list = []
    for at in attribution.find_by_learning_unit(a_learning_unit):
        tutor_list.append(at.tutor)
    return tutor_list


def find_by_id(tutor_id):
    return Tutor.objects.get(id=tutor_id)


def find_responsible(a_learning_unit):
    # S'il y a un seul enseignant => c'est cet enseignant
    # S'il y a plusieurs enseignants et un coordinateur => c'est le coordinateur
    # S'il y a plusieurs enseignants et pas de coordinateur => premier enseignant par l'ordre alphabétique
    attribution_list = attribution.find_by_learning_unit(a_learning_unit)

    if attribution_list and len(attribution_list) > 0:
        if len(attribution_list) == 1:
            return attribution_list[0].tutor
        else:
            for lu_attribution in attribution_list:
                if lu_attribution.function == 'COORDINATOR':
                    return lu_attribution.tutor
            return attribution_list[0].tutor
    return None


def find_by_program_manager(programme_manager):
    """
    To find all the tutors managed by a program manager
    """
    academic_yr = academic_year.current_academic_year()
    program_mgr_list= program_manager.find_by_user(programme_manager)
    tutor_list = []
    for program_mgr in program_mgr_list:
        if program_mgr.offer_year:
            sessions = session_exam.find_sessions_by_offer(program_mgr.offer_year, academic_yr, None)
            for session in sessions:
                learning_unit = session.learning_unit_year.learning_unit
                enrollments = exam_enrollment.find_exam_enrollments_drafts_by_session(session)
                if enrollments and len(enrollments) > 0:
                    responsible_tutor = find_responsible(learning_unit)
                    if responsible_tutor is not None:
                        if responsible_tutor not in tutor_list:
                            tutor_list.append(responsible_tutor)
    return find_by_list(tutor_list)


def find_by_list(list):
    """
    To order tutors by name
    """
    ids =  []
    for t in list:
        ids.append(t.id)

    return  Tutor.objects.filter(id__in=ids).order_by('person__last_name', 'person__first_name')


