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
from django.contrib.auth.decorators import login_required, user_passes_test
from attribution import models as mdl_attr
from base import models as mdl_base
from base.views import layout


def is_faculty_admin(user):
    a_faculty_administrator = mdl_base.entity_manager.find_entity_manager_by_user(user)
    return a_faculty_administrator if a_faculty_administrator else False


@login_required
@user_passes_test(is_faculty_admin)
def scores_responsible(request):
    a_faculty_administrator = mdl_base.entity_manager.find_entity_manager_by_user(request.user)
    attributions = mdl_attr.attribution.find_all_distinct_children(a_faculty_administrator.structure)
    academic_year = mdl_base.academic_year.current_academic_year()
    return layout.render(request, 'scores_responsible.html', {"learning_unit_year_acronym": a_faculty_administrator.structure.acronym,
                                                              "attributions": attributions,
                                                              "academic_year": academic_year,
                                                              "init": "0"})


@login_required
@user_passes_test(is_faculty_admin)
def scores_responsible_search(request):
    a_faculty_administrator = mdl_base.entity_manager.find_entity_manager_by_user(request.user)
    attributions = mdl_attr.attribution.find_all_distinct_children(a_faculty_administrator.structure)
    academic_year = mdl_base.academic_year.current_academic_year()
    attributions_searched = mdl_attr.attribution.search_scores_responsible(
        learning_unit_title=request.POST.get('learning_unit_title'),
        course_code=request.POST.get('course_code'),
        attributions=attributions,
        tutor=request.POST.get('tutor'),
        scores_responsible=request.POST.get('scores_responsible'))
    dict_attribution = create_attributions_list(attributions_searched)
    return layout.render(request, 'scores_responsible.html', {"learning_unit_year_acronym": a_faculty_administrator.structure.acronym,
                                                              "attributions": attributions,
                                                              "academic_year": academic_year,
                                                              "dict_attribution": dict_attribution,
                                                              "learning_unit_title": request.POST.get('learning_unit_title'),
                                                              "course_code": request.POST.get('course_code'),
                                                              "tutor": request.POST.get('tutor'),
                                                              "scores_responsible": request.POST.get('scores_responsible'),
                                                              "init": "1"})


def create_attributions_list(attributions):
    dict_attribution = dict()
    for attribution in attributions:
        tutors = mdl_attr.attribution.find_all_tutors_by_learning_unit_year(attribution.learning_unit_year)
        dict_attribution.update({attribution: [attribution.learning_unit_year.id,
                                               attribution.learning_unit_year.structure.acronym,
                                               attribution.learning_unit_year.acronym,
                                               attribution.learning_unit_year.title,
                                               tutors]})
    return dict_attribution


def scores_responsible_list(request):
    list_course_code = request.GET['course_code']
    return list_course_code


@login_required
@user_passes_test(is_faculty_admin)
def scores_responsible_management(request, pk):
    a_learning_unit_year = mdl_base.learning_unit_year.find_by_id(pk)
    attributions = mdl_attr.attribution.find_all_responsible_by_learning_unit_year(a_learning_unit_year)
    academic_year = mdl_base.academic_year.current_academic_year()
    if request.POST:
        return layout.render(request, 'scores_responsible_edit.html',
                             {'learning_unit_year': a_learning_unit_year,
                              'attributions': attributions,
                              "academic_year": academic_year,
                              'course_code': request.POST.get('course_code'),
                              'learning_unit_title': request.POST.get('learning_unit_title'),
                              'tutor': request.POST.get('tutor'),
                              'scores_responsible': request.POST.get('scores_responsible')})


@login_required
@user_passes_test(is_faculty_admin)
def scores_responsible_add(request, pk):
    if request.POST.get('action') == "add":
        a_learning_unit_year = mdl_base.learning_unit_year.find_by_id(pk)
        mdl_attr.attribution.clear_responsible_by_learning_unit_year(a_learning_unit_year)
        if request.POST.get('a_tutor'):
            prf_id = request.POST.get('a_tutor').strip('prf_')
            attribution = mdl_attr.attribution.find_by_id(prf_id)
            attributions = mdl_attr.attribution.Attribution.objects \
                .filter(learning_unit_year=attribution.learning_unit_year) \
                .filter(tutor=attribution.tutor)
            for a_attribution in attributions:
                a_attribution.score_responsible = True
                a_attribution.save()
    return scores_responsible_search(request)
