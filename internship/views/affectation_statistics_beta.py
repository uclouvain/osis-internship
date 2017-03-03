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
import sys
from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from internship import models as mdl_internship
from datetime import datetime

@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def internship_affectation_statistics_generate(request):
    """ Generate new solution, save it in the database, redirect back to the page 'internship_affectation_statistics'"""
    if request.method == 'POST':
        if request.POST['executions'] != "":
            start_date_time = datetime.now()
            cost = sys.maxsize
            for i in range(0, int(request.POST['executions'])):
                pass
        return redirect(reverse('internship_affectation_statistics'))
