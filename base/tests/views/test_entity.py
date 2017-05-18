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
import datetime
import json
from base.models.entity import Entity
from base.serializers import EntitySerializer
from base.tests.factories.entity import EntityFactory
from base.tests.factories.entity_address import EntityAddressFactory
from base.tests.factories.entity_version import EntityVersionFactory
from base.tests.factories.organization import OrganizationFactory
from base.tests.factories.user import SuperUserFactory
from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from rest_framework.test import APITestCase


class EntityViewTestCase(APITestCase):

    def setUp(self):
        self.entities = [EntityFactory() for x in range(3)]
        user = SuperUserFactory()
        token = Token.objects.create(user=user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    def test_get_all_entities(self):
        response = self.client.get(reverse('get_post_entities'))
        entities = Entity.objects.all()
        serializer = EntitySerializer(entities, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_valid_single_entity(self):
        response = self.client.get(reverse('get_entity', kwargs={'pk': self.entities[0].pk}))
        entity = Entity.objects.get(pk=self.entities[0].pk)
        serializer = EntitySerializer(entity)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_invalid_single_entity(self):
        response = self.client.get(reverse('get_entity', kwargs={'pk': 65465465}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_valid_entity(self):
        organization = OrganizationFactory()
        addresses = [EntityAddressFactory() for x in range(2)]
        version = EntityVersionFactory()
        parent = EntityFactory()
        valid_entity = {
            'organization': organization.id,
            'external_id': "01234567",
            'link_to_parent': [
                {
                    "parent": parent.id,
                    "start_date": datetime.date(2015, 1, 1).isoformat(),
                    "end_date": datetime.date(2015, 12, 31).isoformat()
                },
            ],
            'entityaddress_set': [
                {
                    "label": addresses[0].label,
                    "location": addresses[0].location,
                    "postal_code": addresses[0].postal_code,
                    "city": addresses[0].city,
                    "country": addresses[0].country
                },
                {
                    "label": addresses[1].label,
                    "location": addresses[1].location,
                    "postal_code": addresses[1].postal_code,
                    "city": addresses[1].city,
                    "country": addresses[1].country
                }
            ],
            'entityversion_set': [
                {
                    "title": version.title,
                    "acronym": version.acronym,
                    "entity_type": version.entity_type,
                    "start_date": datetime.date(2015, 1, 1).isoformat(),
                    "end_date": datetime.date(2015, 12, 31).isoformat()
                }
            ]
        }
        response = self.client.post(
            reverse('get_post_entities'),
            data=json.dumps(valid_entity),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_invalid_entity(self):
        invalid_entity = {
            'organization': 'zfeinvzepn',
        }
        response = self.client.post(
            reverse('get_post_entities'),
            data=json.dumps(invalid_entity),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
