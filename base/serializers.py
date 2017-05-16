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
from rest_framework import serializers
from base.models.entity import Entity
from base.models.entity_address import EntityAddress
from base.models.entity_link import EntityLink
from base.models.entity_version import EntityVersion


class EntityAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntityAddress
        fields = ('label', 'location', 'postal_code', 'city', 'country')


class EntityLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntityLink
        fields = ('parent', 'start_date', 'end_date')


class EntityVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntityVersion
        fields = ('acronym', 'title', 'entity_type', 'start_date', 'end_date',)


class EntitySerializer(serializers.ModelSerializer):
    entityaddress_set = EntityAddressSerializer(many=True)
    link_to_parent = EntityLinkSerializer(many=True)
    entityversion_set = EntityVersionSerializer(many=True)

    class Meta:
        model = Entity
        fields = ('id', 'organization', 'external_id', 'entityaddress_set', 'link_to_parent', 'entityversion_set')

    def create(self, validated_data):
        addresses_data = validated_data.pop('entityaddress_set')
        link_to_parent_data = validated_data.pop('link_to_parent')
        versions_data = validated_data.pop('entityversion_set')

        entity = Entity.objects.create(**validated_data)

        for address_data in addresses_data:
            EntityAddress.objects.create(entity=entity, **address_data)

        for link_data in link_to_parent_data:
            try:
                EntityLink.objects.create(child=entity, **link_data)
            except AttributeError:  # TODO : Décider que faire en cas d'erreur (link non-créé)
                pass

        for version_data in versions_data:
            try:
                EntityVersion.objects.create(entity=entity, **version_data)
            except AttributeError:  # TODO : Décider que faire en cas d'erreur (version non-créée)
                pass

        return entity
