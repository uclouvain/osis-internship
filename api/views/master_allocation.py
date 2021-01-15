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
from rest_framework.generics import get_object_or_404

from internship.api.serializers.master_allocation import MasterAllocationSerializer
from internship.models.internship_master import InternshipMaster
from internship.models.master_allocation import MasterAllocation
from internship.models.period import Period


class MasterAllocationList(generics.ListAPIView):
    """
       Return a list of master allocations with optional filtering.
    """
    name = 'master-allocation-list'
    serializer_class = MasterAllocationSerializer
    queryset = MasterAllocation.objects.all().select_related('master')
    search_fields = (
        'organization', 'specialty'
    )
    ordering_fields = (
        'birth_date', 'specialty'
    )
    ordering = (
        'organization',
    )  # Default ordering

    def get_queryset(self):
        master = get_object_or_404(InternshipMaster, uuid=self.kwargs['uuid'])
        qs = MasterAllocation.objects.filter(master=master).select_related('organization', 'specialty')
        if self.request.query_params.get('current'):
            current_cohort = Period.active.first().cohort
            qs = qs.filter(specialty__cohort=current_cohort, organization__cohort=current_cohort)
        return qs


class MasterAllocationDetail(generics.RetrieveAPIView):
    """
        Return the detail of the internship master allocation.
    """
    name = 'master-allocation-detail'
    serializer_class = MasterAllocationSerializer
    queryset = MasterAllocation.objects.all()
    lookup_field = 'uuid'
