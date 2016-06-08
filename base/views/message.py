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
from django.contrib.auth.decorators import login_required

from base import models
from base.forms import MessageHistorySearchForm
from base.utils import send_mail
from base.views import layout


@login_required
def messages(request):
    return layout.render(request, "messages.html", {})


@login_required
def messages_history_index(request):
    return layout.render(request, "messages_history.html", {'form': MessageHistorySearchForm()})


@login_required
def message_history_read(request, message_history_id):
    message_history = models.message_history.find_by_id(message_history_id)
    return layout.render(request, "message_history.html", {"message_history": message_history})


@login_required
def send_message_again(request, message_history_id):
    message_history = send_mail.send_again(message_history_id)
    return layout.render(request, "message_history.html", {'message_history': message_history})


@login_required
def find_messages_history(request):
    form = MessageHistorySearchForm(request.POST)
    messages_history = []
    if form.is_valid():
        messages_history = models.message_history.search(**form.cleaned_data)
    data = {'form': form,
            'messages_history': messages_history}
    return layout.render_to_response(request, "messages_history.html", data)




