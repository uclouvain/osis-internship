##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2017 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from attribution import models as mdl_attr
from attribution.models import attribution
from base.models import entity_manager, learning_unit_year
from base.views import layout


def is_faculty_admin(user):
    a_faculty_administrator = entity_manager.find_entity_manager_by_user(user)
    return a_faculty_administrator if a_faculty_administrator else False


@login_required
@user_passes_test(is_faculty_admin)
def scores_responsible(request):
    a_faculty_administrator = entity_manager.find_entity_manager_by_user(request.user)
    attributions = attribution.find_all_distinct_children(a_faculty_administrator.structure)
    return layout.render(request, 'scores_responsible.html', {"learning_unit_year_acronym": a_faculty_administrator.structure.acronym,
                                                              "attributions": attributions})


@login_required
@user_passes_test(is_faculty_admin)
def scores_responsible_search(request):
    a_faculty_administrator = entity_manager.find_entity_manager_by_user(request.user)
    attributions = attribution.find_all_distinct_children(a_faculty_administrator.structure)
    if request.GET.get('entity') == "all_entities":
        attributions_searched = mdl_attr.attribution.search_scores_responsible(
            learning_unit_title=request.GET.get('learning_unit_title'),
            course_code=request.GET.get('course_code'),
            attributions=attributions,
            entity=request.GET.get('entity'),
            tutor=request.GET.get('tutor'),
            scores_responsible=request.GET.get('scores_responsible'))
    else:
        attributions_searched = mdl_attr.attribution.search_scores_responsible(
            learning_unit_title=request.GET.get('learning_unit_title'),
            course_code=request.GET.get('course_code'),
            attributions=None,
            entity=request.GET.get('entity'),
            tutor=request.GET.get('tutor'),
            scores_responsible=request.GET.get('scores_responsible'))
    dict_attribution = create_attributions_list(attributions_searched)
    return layout.render(request, 'scores_responsible.html', {"attributions": attributions,
                                                              "dict_attribution": dict_attribution,
                                                              "acronym": request.GET.get('entity'),
                                                              "learning_unit_title": request.GET.get('learning_unit_title'),
                                                              "course_code": request.GET.get('course_code'),
                                                              "tutor": request.GET.get('tutor'),
                                                              "scores_responsible": request.GET.get('scores_responsible')})


def create_attributions_list(attributions):
    dict_attribution = dict()
    for attribution in attributions:
        tutor_number = mdl_attr.attribution.find_tutor_number(attribution)
        responsible = mdl_attr.attribution.find_all_responsibles_by_learning_unit_year(attribution.learning_unit_year)
        dict_attribution.update({attribution: [attribution.learning_unit_year.id,
                                               attribution.learning_unit_year.structure.acronym,
                                               attribution.learning_unit_year.acronym,
                                               attribution.learning_unit_year.title,
                                               tutor_number, responsible]})
    return dict_attribution


def scores_responsible_list(request):
    list_course_code = request.GET['course_code']
    return list_course_code


@login_required
@user_passes_test(is_faculty_admin)
def scores_responsible_management(request, pk):
    a_learning_unit_year = learning_unit_year.find_by_id(pk)
    attributions = mdl_attr.attribution.find_all_responsible_by_learning_unit_year(a_learning_unit_year)
    return layout.render(request, 'scores_responsible_edit.html',
                         {'learning_unit_year': a_learning_unit_year,
                          'attributions': attributions})


@login_required
@user_passes_test(is_faculty_admin)
def scores_responsible_add(request, pk):
    a_learning_unit_year = learning_unit_year.find_by_id(pk)
    mdl_attr.attribution.clear_responsible_by_learning_unit_year(a_learning_unit_year)
    if request.GET:
        for tutor in request.GET:
            prf_id = tutor.strip('prf_')
            attribution = mdl_attr.attribution.find_by_id(prf_id)
            if request.GET.get(tutor):
                attribution.score_responsible = True
                attribution.save()
    return redirect('scores_responsible')
