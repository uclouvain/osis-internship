##############################################################################
#
# OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2017 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
import factory
import factory.fuzzy
from datetime import date
from assistant.test.factories.academic_assistant import AcademicAssistantFactory
from base.tests.factories.academic_year import AcademicYearFactor
from assistant.models.enums import assistant_type


class AssistantMandateFactory(factory.DjangoModelFactory):
    class Meta:
        model = 'assistant.AssistantMandate'

    assistant = factory.SubFactory(AcademicAssistantFactory)
    academic_year = factory.SubFactory(AcademicYearFactory)
    assistant_type = factory.Iterator(assistant_type.ASSISTANT_TYPES, getter=lambda c: c[0])
    #fulltime_equivalent = factory.fuzzy.FuzzyDecimal(0, 1, 2)
    fulltime_equivalent = factory.Iterator([0.25, 0.33, 0.5, 0.75, 1])
    entry_date = factory.fuzzy.FuzzyDateTime(datetime.datetime(2000, 9, 15), force_year=date.today().year - 2)
    end_date = factory.fuzzy.FuzzyDateTime(datetime.datetime(date.today().year, 9, 14))
    sap_id = factory.fuzzy.FuzzyText(length=7, chars=string.ascii_numbers,prefix='')

