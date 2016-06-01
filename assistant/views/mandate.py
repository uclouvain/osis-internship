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
    with codecs.open('osis/assistant/views/data_assistant.csv', encoding='utf-8') as csvfile:
        row = csv.reader(csvfile, delimiter=';')
        imported_counter = 0
        error_counter = 0
        for columns in row:
            if len(columns) > 0:
                person = mdl.person.find_by_global_id(columns[4].strip())
                if person:
                    assistant = academic_assistant.AcademicAssistant()
                    assistant.person = person
                    assistant.position_id = columns[3].strip()
                    
                    try:
                        assistant.save()
                    except IntegrityError:
                            print('Duplicated : %s - %s' % (assistant, person))
                    imported_counter += 1
                else:
                    error_counter += 1
                    print(u'"%s", "%s", ("%s")"' % (columns[6], columns[5], columns[4]))
        print(u'%d assistants imported.' % imported_counter)
        print(u'%d assistants not imported.' % error_counter)
    return layout.render(request, "load_mandates.html", {'imported_counter': imported_counter,
                                                         'error_counter': error_counter})             
 



