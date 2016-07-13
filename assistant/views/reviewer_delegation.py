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
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect
from assistant.models import assistant_mandate, reviewer, mandate_structure
from base.models import academic_year, structure
from assistant.forms import ReviewerDelegationForm
from django.views.generic import ListView
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ObjectDoesNotExist

class StructuresListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    context_object_name = 'reviewer_structures_list'
    template_name = 'reviewer_structures_list.html'
    form_class = ReviewerDelegationForm

    def test_func(self):
        try:
            return reviewer.Reviewer.objects.get(Q(person=self.request.user.person) &
                                                   (Q(role="SUPERVISION") | Q(role="RESEARCH")))
        except ObjectDoesNotExist:
            return False
    
    def get_login_url(self):
        return reverse('assistants_home')

    def get_queryset(self):
        rev = reviewer.Reviewer.objects.get(person=self.request.user.person)
        queryset = structure.Structure.objects.filter(Q(id=rev.structure.id) | Q(part_of_id=rev.structure.id))
        return queryset

    def get_context_data(self, **kwargs):
        context = super(StructuresListView, self).get_context_data(**kwargs)
        context['year'] = academic_year.current_academic_year().year
        context['current_reviewer'] = reviewer.Reviewer.objects.get(person=self.request.user.person)
        return context

def user_is_reviewer_and_can_delegate(user):
    """Use with a ``user_passes_test`` decorator to restrict access to
    authenticated users who are reviewer and can delegate."""

    try:
        if user.is_authenticated():
            return reviewer.Reviewer.objects.get(Q(person=user.person) &
                                                   (Q(role="SUPERVISION") | Q(role="RESEARCH")))
    except ObjectDoesNotExist:
        return False

@user_passes_test(user_is_reviewer_and_can_delegate, login_url='assistants_home')
def addReviewerForStructure(request, structure_id):
    related_structure = structure.find_by_id(structure_id)
    year = academic_year.current_academic_year().year
    try:
        reviewer.Reviewer.objects.get(Q(person=request.user.person) & Q(structure=related_structure))
    except:
        return redirect('assistants_home')
    if request.POST:
        form = ReviewerDelegationForm(data=request.POST)
        if form.is_valid():
            
            form.save()
            return redirect('reviewer_delegation')
        else:
            return render(request, "reviewer_add_reviewer.html", {'form': form,
                                                          'year': year,
                                                          'related_structure': related_structure})
    else:   
        reviewer_role = reviewer.Reviewer.objects.get(person=request.user.person).role
        if reviewer_role == "SUPERVISION":
            role = "SUPERVISION_ASSISTANT"
        else: 
            role = "RESEARCH_ASSISTANT" 
        form = ReviewerDelegationForm(initial={'structure': related_structure,
                                           'year': year,
                                           'role': role,
                                       })
        return render(request, "reviewer_add_reviewer.html", {'form': form,
                                                          'year': year,
                                                          'related_structure': related_structure}) 
