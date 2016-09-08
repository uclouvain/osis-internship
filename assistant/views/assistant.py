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
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.urlresolvers import reverse
from django.forms import forms
from base.models import person, academic_year
from django.core.exceptions import ObjectDoesNotExist
from assistant.models import academic_assistant, assistant_mandate
from django.views.generic.list import ListView
from django.views.generic.edit import FormMixin
from django.http.response import HttpResponseRedirect
from assistant.models import settings


class AssistantMandatesListView(LoginRequiredMixin, UserPassesTestMixin, ListView, FormMixin):
    context_object_name = 'assistant_mandates_list'
    template_name = 'assistant_mandates.html'
    form_class = forms.Form

    def test_func(self):
        try:
            if settings.access_to_procedure_is_open():
                return academic_assistant.AcademicAssistant.objects.get(person=self.request.user.person)
            else:
                return False
        except ObjectDoesNotExist:
            return False

    def get_login_url(self):
        return reverse('access_denied')

    def get_queryset(self):
        assistant = academic_assistant.find_by_person(
            person.find_by_user(self.request.user))
        this_academic_year = academic_year.current_academic_year()
        return assistant_mandate.find_mandate_by_academic_assistant(assistant)

    def get_context_data(self, **kwargs):
        context = super(AssistantMandatesListView,
                        self).get_context_data(**kwargs)
        context['assistant'] = academic_assistant.find_by_person(
            person.find_by_user(self.request.user))
        return context


def user_is_assistant_and_procedure_is_open(user):
    """Use with a ``user_passes_test`` decorator to restrict access to
    authenticated users who are assistant.
    The procedure must be open"""

    try:
        if user.is_authenticated() and settings.access_to_procedure_is_open():
            return academic_assistant.find_by_person(user.person)
        else:
            return False
    except ObjectDoesNotExist:
        return False


@user_passes_test(user_is_assistant_and_procedure_is_open, login_url='access_denied')
def mandate_change_state(request, mandate_id):
    mandate = assistant_mandate.find_mandate_by_id(mandate_id)
    if 'bt_mandate_accept' in request.POST:
        mandate.state = 'TRTS'
    elif 'bt_mandate_decline' in request.POST:
        mandate.state = 'DECLINED'
    mandate.save()
    return HttpResponseRedirect(reverse('assistant_mandates'))
