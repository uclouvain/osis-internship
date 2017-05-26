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
from attribution import models as mdl_attr
from base import models as mdl_base
from attribution.models.enums import function


def update_attributions_responsibles():
    academic_year = mdl_base.academic_year.current_academic_year()
    attributions = mdl_attr.attribution.Attribution.objects\
        .select_related('learning_unit_year')\
        .filter(learning_unit_year__academic_year=academic_year).order_by('learning_unit_year__id', 'tutor__person__last_name', 'tutor__person__first_name')
    dict_attribution = dict()
    for attribution in attributions:
        key = attribution.learning_unit_year.id
        dict_attribution.setdefault(key, []).append(attribution)
    for key, attributions in dict_attribution.items():
        responsibles = [responsible for responsible in attributions if responsible.score_responsible]
        if len(responsibles) == 0:
            coordinators = [coordinator for coordinator in attributions if coordinator.function == function.COORDINATOR]
            if len(coordinators) == 0:
                select_default_responsible(attributions, attributions)
            else:
                select_default_responsible(attributions, coordinators)
        elif len(responsibles) == 1:
            select_default_responsible(attributions, responsibles)
        else:
            coordinators = [coordinator for coordinator in responsibles if coordinator.function == function.COORDINATOR]
            if len(coordinators) == 0:
                select_default_responsible(attributions, responsibles)
            else:
                select_default_responsible(attributions, coordinators)


def select_default_responsible(attributions, coordinators):
    for attribution in attributions:
        if attribution.tutor == coordinators[0].tutor:
            attribution.score_responsible = True
            attribution.save()
        else:
            attribution.score_responsible = False
            attribution.save()


update_attributions_responsibles()
