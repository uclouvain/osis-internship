##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)
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
from enum import Enum
from internship.models.enums.choice_type import ChoiceType


class Costs(Enum):
    FIRST_CHOICE = 0
    SECOND_CHOICE = 1
    THIRD_CHOICE = 2
    FORTH_CHOICE = 3
    PRIORITY = 0
    IMPOSED = 10
    ERROR = 1000


COSTS = {ChoiceType.FIRST_CHOICE.value: Costs.FIRST_CHOICE.value,
         ChoiceType.SECOND_CHOICE.value: Costs.SECOND_CHOICE.value,
         ChoiceType.THIRD_CHOICE.value: Costs.THIRD_CHOICE.value,
         ChoiceType.FORTH_CHOICE.value: Costs.FORTH_CHOICE.value,
         ChoiceType.PRIORITY.value: Costs.PRIORITY.value,
         ChoiceType.IMPOSED.value: Costs.IMPOSED.value,
         ChoiceType.ERROR.value: Costs.ERROR.value}
