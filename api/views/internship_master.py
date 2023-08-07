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
from rest_framework.response import Response

from internship.api.serializers.internship_master import InternshipMasterSerializer
from internship.api.serializers.master_allocation import MasterAllocationSerializer
from internship.models.enums.user_account_status import UserAccountStatus
from internship.models.internship_master import InternshipMaster
from internship.models.master_allocation import MasterAllocation
from internship.models.period import Period


class InternshipMasterListCreate(generics.ListCreateAPIView):
    """
       Return a list of internship masters with optional filtering or create one.
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


class InternshipMasterUpdateDetail(generics.RetrieveUpdateAPIView):
    """
        Return the detail of the internship master or create one.
    """
    name = 'master-detail'
    serializer_class = InternshipMasterSerializer
    queryset = InternshipMaster.objects.all()
    lookup_field = 'uuid'


class InternshipMasterActivateAccount(generics.GenericAPIView):
    """
        Set internship master's user account status to ACTIVE
    """
    name = 'master-activate-account'
    serializer_class = InternshipMasterSerializer
    queryset = InternshipMaster.objects.all()
    lookup_field = 'uuid'

    """
    Update user account status.
    """
    def post(self, request, *args, **kwargs):
        master = self.get_object()
        master.user_account_status = UserAccountStatus.ACTIVE.name
        master.save()
        serializer = self.get_serializer(master)
        return Response(serializer.data)


class InternshipMasterAllocationListCreate(generics.ListCreateAPIView):
    """
       Return a list of master allocations with optional filtering.
    """
    name = 'master-allocation-list'
    serializer_class = MasterAllocationSerializer
    queryset = MasterAllocation.objects.all()
    search_fields = (
        'organization', 'specialty'
    )
    ordering_fields = ('specialty')
    ordering = (
        'organization',
    )  # Default ordering

    def get_queryset(self):
        master = get_object_or_404(InternshipMaster, uuid=self.kwargs['uuid'])
        qs = MasterAllocation.objects.filter(master=master).select_related(
            'master__person', 'organization__country', 'specialty__cohort'
        )
        if self.request.query_params.get('current'):
            active_periods = Period.active.all()
            current_cohorts = (
                active_periods.values('cohort_id')
                if active_periods
                else Period.past.all().values_list('cohort_id').first()
            )
            qs = qs.filter(specialty__cohort_id__in=current_cohorts, organization__cohort_id__in=current_cohorts)
        return qs
