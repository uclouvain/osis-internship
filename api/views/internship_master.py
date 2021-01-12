##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2020 Université catholique de Louvain (http://www.uclouvain.be)
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
from rest_framework import generics

from internship.api.serializers.internship_master import InternshipMasterSerializer
from internship.models.internship_master import InternshipMaster


class InternshipMasterList(generics.ListAPIView):
    """
       Return a list of internship masters with optional filtering.
    """
    name = 'master-list'
    serializer_class = InternshipMasterSerializer
    queryset = InternshipMaster.objects.all()
    search_fields = (
        'person__last_name', 'person__first_name', 'person__email'
    )
    ordering_fields = (
        'birth_date',
    )
    ordering = (
        'person__last_name',
    )  # Default ordering


class InternshipMasterDetail(generics.RetrieveAPIView):
    """
        Return the detail of the internship master.
    """
    name = 'master-detail'
    serializer_class = InternshipMasterSerializer
    queryset = InternshipMaster.objects.all()
    lookup_field = 'uuid'
