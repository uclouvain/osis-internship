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
from django.db import IntegrityError
import csv, codecs
from assistant.forms import MandateForm
from base.views import layout
from assistant.models import assistant_mandate, academic_assistant
from base import models as mdl
from base.views.layout import render_to_response
from django.http.response import HttpResponseRedirect



@login_required
def mandate_edit(request, mandate_id):
    mandate = assistant_mandate.find_mandate_by_id(mandate_id)
    form = MandateForm(initial={'comment': mandate.comment, 
                                'renewal_type': mandate.renewal_type,
                                'absences': mandate.absences,
                                'other_status': mandate.other_status,
                                'contract_duration': mandate.contract_duration,
                                'contract_duration_fte': mandate.contract_duration_fte
                                })
    return layout.render(request, 'mandate_form.html', {'mandate': mandate,
                                                'form': form})


def mandate_save(request, mandate_id):
    form = MandateForm(data=request.POST)
    mandate = assistant_mandate.find_mandate_by_id(mandate_id)
    # get the screen modifications
    if request.POST['comment']:
        mandate.comment = request.POST['comment']
        mandate.absences = request.POST['absences']
    else:
        mandate.comment = None
        mandate.absences = None
    if request.POST['absences']:
        mandate.absences = request.POST['absences']
    else:
        mandate.absences = None
    if request.POST['other_status']:
        mandate.other_status = request.POST['other_status']
    else:
        mandate.other_status = None
    mandate.renewal_type = request.POST['renewal_type']
    if form.is_valid():
        mandate.save()
        return mandate_edit(request, mandate.id)
    else:
        return layout.render(request, "mandate_form.html", {'mandate': mandate,
                                                                 'form': form})    



def load_mandates(request):
    imported_assistants_counter = 0
    imported_mandates_counter = 0
    error_counter = 0
    if(request.POST):
        with codecs.open('osis/assistant/views/data_assistant.csv', encoding='utf-8') as csvfile:
            row = csv.reader(csvfile, delimiter=';')
            for columns in row:
                if len(columns) > 0:
                    person = mdl.person.find_by_global_id(columns[5].strip())
                    print('%s' % (person)) 
                    if person:
                        assistant = academic_assistant.AcademicAssistant()
                        assistant.person = person
                        mandate = assistant_mandate.AssistantMandate()
                        fte = columns[8].strip().replace(",", ".");
                        mandate.fulltime_equivalent = fte
                        mandate.position_id = columns[3].strip()  
                        mandate.sap_id = columns[4].strip()  
                        mandate.entry_date = columns[9].strip()
                        mandate.end_date = columns[10].strip()
                        mandate.assistant_type = columns[11].strip()
                        mandate.grade = columns[12].strip()
                        mandate.scale = columns[13].strip()
                        mandate.contract_duration = columns[14].strip()
                        mandate.contract_duration_fte = columns[15].strip()
                        mandate.renewal_type = columns[16].strip()
                        mandate.absences =columns[17].strip()
                        mandate.comment =columns[18].strip()
                        mandate.other_status = columns[19].strip()
                        mandate.state='TO_DO'
                        mandate.research_percent=0
                        mandate.tutoring_percent=0
                        mandate.service_activities_percent=0
                        mandate.formation_activities_percent=0
                        mandate.faculty_representation=0
                        mandate.institute_representation=0
                        mandate.sector_representation=0
                        mandate.governing_body_representation=0
                        mandate.corsci_representation=0
                        mandate.students_service=0
                        mandate.infrastructure_mgmt_service=0
                        mandate.events_organisation_service=0
                        mandate.publishing_field_service=0
                        mandate.scientific_jury_service=0
                        this_academic_year = mdl.academic_year.current_academic_year()
                        mandate.academic_year=this_academic_year
                        mandate.appeal='NONE'
                        mandate.special=False
                        try:
                            assistant.save()
                            imported_assistants_counter += 1
                        except IntegrityError:
                            print('Duplicated : %s - %s' % (assistant, person))
                        try:
                            mandate.assistant=academic_assistant.find_by_person(person)
                            mandate.save()
                            imported_mandates_counter += 1
                        except IntegrityError:
                            print('Duplicated : %s - %s' % (assistant, person))
                    else:
                        error_counter += 1
    return layout.render(request, "load_mandates.html", {'imported_assistants': imported_assistants_counter,
                                                         'imported_mandates': imported_mandates_counter,
                                                         'error_counter': error_counter})             
 



