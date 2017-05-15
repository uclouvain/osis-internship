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
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from base.models.entity import Entity
from base.serializers import EntitySerializer


@api_view(['GET', 'DELETE', 'PUT'])
def get_delete_update_entity(request, pk):
    try:
        entity = Entity.objects.get(pk=pk)
    except Entity.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    # get details of a single entity
    if request.method == 'GET':
        serializer = EntitySerializer(entity)
        return Response(serializer.data)
    # delete a single entity
    elif request.method == 'DELETE':
        return Response({})
    # update details of a single entity
    elif request.method == 'PUT':
        return Response({})


@api_view(['GET', 'POST'])
def get_post_entities(request):
    # get all entities
    if request.method == 'GET':
        entities = Entity.objects.all()
        serializer = EntitySerializer(entities, many=True)
        return Response(serializer.data)

    # insert a new record for an entity
    elif request.method == 'POST':
        entity_data = {
            'organization': request.data.get('organization'),
            'entityaddress_set': request.data.get('entityaddress_set'),
            'link_to_parent': request.data.get('link_to_parent'),
            'entityversion_set': request.data.get('entityversion_set'),
        }
        entity_serializer = EntitySerializer(data=entity_data)

        if entity_serializer.is_valid():
            entity_serializer.save()
            return Response(entity_serializer.data, status=status.HTTP_201_CREATED)
        return Response(entity_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
