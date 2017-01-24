##############################################################################
#
# OSIS stands for Open Student Information System. It's an application
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
from django.contrib.auth.decorators import login_required, permission_required
from base import models as mdl
from base.forms import TextLabelForm
from . import layout


@login_required
@permission_required('base.can_access_textlabel', raise_exception=True)
def text_label(request):
    academic_yr = None
    code = ""

    academic_years = mdl.academic_year.find_academic_years()
    academic_yr_calendar = mdl.academic_year.current_academic_year()

    if academic_yr_calendar:
        academic_yr = academic_yr_calendar.id
    return layout.render(request, "text_label.html", {'academic_year': academic_yr,
                                                          'code': code,
                                                          'academic_years': academic_years,
                                                          'learning_units': [],
                                                          'init': "1"})


@login_required
@permission_required('base.can_access_textlabel', raise_exception=True)
def text_label_search(request):
    """
    Learning units search
    """
    # criteria
    academic_year = request.GET['academic_year']
    code = request.GET['code']
    if academic_year is None:
        academic_year_calendar = mdl.academic_year.current_academic_year()
        if academic_year_calendar:
            academic_year = academic_year_calendar.id

    learning_unts = mdl.learning_unit_year.search(academic_year_id=academic_year,acronym=code)
    academic_years = mdl.academic_year.find_academic_years()

    return layout.render(request, "text_label.html", {'academic_year': int(academic_year),
                                                          'code': code,
                                                          'academic_years': academic_years,
                                                          'learning_units': learning_unts,
                                                          'init': "0"})


def text_label_read_from_entity(request, entity_id):
    text_labels = mdl.text_label.find_text_label_hierarchy(entity_id)
    is_program_manager = mdl.program_manager.is_program_manager(request.user)
    return layout.render(request, "text_label.html", {'text_labels': text_labels,
                                                      'entity_id': entity_id,
                                                      'is_program_manager': is_program_manager})


def text_label_read(request, entity_id, reference_id):
    is_program_manager = mdl.program_manager.is_program_manager(request.user)
    return layout.render(request, "text_label.html", { 'reference_id': reference_id,
                                                       'is_program_manager': is_program_manager})


@login_required
def text_label_new(request, entity_id):
    return text_label_save(request, entity_id, None)


@login_required
def text_label_save(request, entity_id, text_label_id):

    if text_label_id:
        txtlabel = mdl.text_label.find_by_id(text_label_id)
    else:
        txtlabel = mdl.text_label.TextLabel()

    form = TextLabelForm(data=request.POST, instance=txtlabel)
    is_program_manager = mdl.program_manager.is_program_manager(request.user)

    # get the screen modifications
    txtlabel.label = request.POST.get("label", None)
    txtlabel.order = request.POST.get("order", None)

    txtlabel.entity_name = entity_id

    if form.is_valid():
        txtlabel.save()
        return text_label_read_from_entity(request, entity_id)
    else:
        text_labels = mdl.text_label.find_text_label_hierarchy(entity_id)
        return layout.render(request, "text_label.html", {'text_labels': text_labels,
                                                          'is_program_manager': is_program_manager})


@login_required
def text_label_save_parent(request, entity_id, part_of_id):
    txtlabelparent = mdl.text_label.find_by_id(part_of_id)
    txtlabel = mdl.text_label.TextLabel()
    form = TextLabelForm(data=request.POST, instance=txtlabel)
    is_program_manager = mdl.program_manager.is_program_manager(request.user)

    # get the screen modifications
    txtlabel.label = request.POST.get("label", None)
    txtlabel.order = request.POST.get("order", None)

    txtlabel.entity_name = entity_id
    txtlabel.part_of = txtlabelparent

    if form.is_valid():
        txtlabel.save()
        return text_label_read_from_entity(request, entity_id)
    else:
        text_labels = mdl.text_label.find_text_label_hierarchy(entity_id)
        return layout.render(request, "text_label.html", {'text_labels': text_labels,
                                                          'is_program_manager': is_program_manager})
