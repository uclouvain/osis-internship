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
from django.db.models import Max, F, Case, When
from base.models import entity_version, offer_year_entity, entity
from base.models.enums import entity_type


def find_from_offer_year(offer_year):
    return [entity_version.get_last_version(off_year_entity.entity)
            for off_year_entity in offer_year_entity.search(offer_year=offer_year).distinct('entity')]


def find_last_versions_from_entites(entities):
    order_list = [entity_type.SECTOR, entity_type.FACULTY, entity_type.SCHOOL, entity_type.INSTITUTE, entity_type.POLE]
    preserved = Case(*[When(entity_type=pk, then=pos) for pos, pk in enumerate(order_list)])
    return entity.Entity.objects.filter(pk__in=entities).\
        annotate(most_recent_version=Max('entityversion__start_date')).\
        annotate(acronym=F('entityversion__acronym')).annotate(title=F('entityversion__title')). \
        annotate(entity_type=F('entityversion__entity_type')).order_by(preserved)
