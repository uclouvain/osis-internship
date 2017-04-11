##############################################################################
#
# OSIS stands for Open Student Information System. It's an application
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
from attribution import models as mdl_attr
from base.views import layout


def scores_responsibles(request):
    attributions_list = mdl_attr.attribution.Attribution.objects.all()
    attributions = mdl_attr.attribution.find_all_responsibles()
    dict_attribution = dict()
    for attribution in attributions:
        tutor_number = mdl_attr.attribution.find_tutor_number(attribution)
        dict_attribution.update({attribution: [attribution.learning_unit_year.structure.acronym,
                                               attribution.learning_unit_year.acronym,
                                               attribution.learning_unit_year.title,
                                               tutor_number, attribution.tutor]})
    return layout.render(request, 'scores_responsibles.html', {"attributions_list": attributions_list,
                                                               "dict_attribution": dict_attribution})


def scores_responsible_search(request):
    attributions_list = mdl_attr.attribution.Attribution.objects.all().distinct("learning_unit_year")
    attributions = mdl_attr.attribution.search_scores_responsible(learning_unit_title=request.GET['learning_unit_title'],
                                                                  course_code=request.GET['course_code'],
                                                                  entity=request.GET['entity'])
    dict_attribution = dict()
    for attribution in attributions:
        tutor_number = mdl_attr.attribution.find_tutor_number(attribution)
        dict_attribution.update({attribution: [attribution.learning_unit_year.structure.acronym,
                                               attribution.learning_unit_year.acronym,
                                               attribution.learning_unit_year.title,
                                               tutor_number, attribution.tutor]})
    return layout.render(request, 'scores_responsibles.html', {"attributions_list": attributions_list,
                                                               "dict_attribution": dict_attribution})
