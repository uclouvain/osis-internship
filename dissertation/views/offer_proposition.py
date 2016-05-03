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
from django.shortcuts import render, get_object_or_404,redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from pprint import pprint
from base import models as mdl
from dissertation.models.offer_proposition import OfferProposition
from dissertation.models.adviser import Adviser
from dissertation.forms import  OfferPropositionForm
from django.contrib.auth.decorators import user_passes_test

# Used by decorator @user_passes_test(is_manager) to secure manager views
def is_manager(user):
    person = mdl.person.find_by_user(user)
    adviser = Adviser.find_by_person(person)
    return adviser.type == 'MGR'

@login_required
@user_passes_test(is_manager)
def offer_proposition_detail(request, pk):
    offer_proposition = get_object_or_404(OfferProposition, pk=pk)
    person = mdl.person.find_by_user(request.user)
    adviser = Adviser.find_by_person(person)
    return render(request, 'offer_proposition_detail.html', {'offer_proposition': offer_proposition, 'adviser': adviser})

@login_required
@user_passes_test(is_manager)
def manage_proposition_dissertation_edit(request, pk):
    offer_proposition = get_object_or_404(OfferProposition, pk=pk)
    person = mdl.person.find_by_user(request.user)
    adviser = Adviser.find_by_person(person)
    if request.method == "POST":
        form = OfferPropositionForm(request.POST, instance=proposition_dissertation)
        if form.is_valid():
            offer_proposition = form.save(commit=False)
            offer_proposition.save()
            return redirect('offer_proposition_detail', pk=offer_proposition.pk)
    else:
        form = OfferPropositionForm(instance=offer_proposition)
    return render(request, 'offer_proposition_edit.html', {'form': form})
