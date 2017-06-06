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
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from base.models import entity
from base.models import entity_link
from base.models import entity_version
from base.serializers import EntitySerializer


@api_view(['POST'])
def post_entities(request):
    if request.method == 'POST':
        existing_entity = entity.get_by_external_id(request.data.get('external_id'))

        if existing_entity is None:
            return create_full_entity(request)

        else:
            return update_existing_entity(existing_entity, request)
    else:
        return Response(status=status.HTTP_401_UNAUTHORIZED)


def create_full_entity(request):
    entity_data = {
        'organization': request.data.get('organization'),
        'external_id': request.data.get('external_id'),
        'entityaddress_set': request.data.get('entityaddress_set'),
        'link_to_parent': request.data.get('link_to_parent'),
        'entityversion_set': request.data.get('entityversion_set'),
    }
    entity_serializer = EntitySerializer(data=entity_data)
    if entity_serializer.is_valid():
        try:
            entity_serializer.save()
        except AttributeError:
            return Response(data=entity_serializer.errors, status=status.HTTP_406_NOT_ACCEPTABLE)
        return Response(data=entity_serializer.data, status=status.HTTP_201_CREATED)
    return Response(data=entity_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def update_existing_entity(existing_entity, request):
    new_versions_count = create_versions_of_existing_entity(request, existing_entity)
    new_links_count = create_links_of_existing_entity(request, existing_entity)
    entity_serializer = EntitySerializer(existing_entity)
    data = entity_serializer.data
    data['new_versions_count'] = new_versions_count
    data['new_links_count'] = new_links_count
    return Response(data=data, status=status.HTTP_200_OK)


def create_versions_of_existing_entity(request, same_entity):
    new_versions_count = 0
    entityversion_data = request.data.get('entityversion_set')
    for version in entityversion_data:
        same_versions_count = entity_version.count(entity=same_entity,
                                                   title=version.get('title'),
                                                   acronym=version.get('acronym'),
                                                   entity_type=version.get('entity_type'),
                                                   start_date=version.get('start_date'),
                                                   end_date=version.get('end_date')
                                                   )
        if not same_versions_count:
            if create_version(version, same_entity) is not None:
                new_versions_count += 1

    return new_versions_count


def create_version(version, same_entity):
        try:
            new_version = entity_version.EntityVersion.objects.create(entity=same_entity, **version)
        except AttributeError:
            new_version = None
        return new_version


def create_links_of_existing_entity(request, same_entity):
    new_links_count = 0
    link_to_parent_data = request.data.get('link_to_parent')
    for link in link_to_parent_data:
        same_links_count = entity_link.count(child=same_entity,
                                             parent=link.get('parent'),
                                             start_date=link.get('start_date'),
                                             end_date=link.get('end_date')
                                             )
        if not same_links_count:
            if create_link(link, same_entity) is not None:
                new_links_count += 1

    return new_links_count


def create_link(link, same_entity):
        try:
            parent_id = link.pop('parent')
            parent = entity.get_by_internal_id(parent_id)
            new_link = entity_link.EntityLink.objects.create(child=same_entity, parent=parent, **link)
        except AttributeError:
            new_link = None
        return new_link
