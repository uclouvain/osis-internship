##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from decimal import Decimal, Context, Inexact

from base.business import learning_unit_year_with_context
from base.models import learning_unit_year
from base.models.enums import learning_unit_year_subtypes


def update_volumes(learning_unit_year_id, updated_volumes):
    volumes_grouped_by_lunityear = _get_volumes_from_db(learning_unit_year_id)

    # Replace volumes db by volumes entered by user
    volumes_grouped_by_lunityear = [_update_volume(lunityear, updated_volumes) for lunityear in
                                     volumes_grouped_by_lunityear]

    # Check consistency
    #learning_unit_year_parent = _get_learning_unit_parent(volumes_db)



def _get_volumes_from_db(learning_unit_year_id):
    luy = learning_unit_year.find_by_id(learning_unit_year_id)
    return learning_unit_year_with_context.get_with_context(
        learning_container_year_id=luy. learning_container_year
    )


def _get_learning_unit_parent(volumes_grouped_by_lunityear):
    next((lunit_year for lunit_year in volumes_grouped_by_lunityear
          if lunit_year.subtype == learning_unit_year_subtypes.FULL), None)


def _update_volume(lunityear, updated_volumes):
    updated_volume = updated_volumes.get(lunityear.id)
    if updated_volume:
        for component, data in lunityear.components.items():
            pass


def _validate_decimals(volume):
    volume_formated = _format_volume_to_decimal(volume)

    try:
        # Ensure that we cannot have more than 2 decimal
        return volume_formated.quantize(Decimal(10) ** -2, context=Context(traps=[Inexact]))
    except:
        raise ValueError("score_have_more_than_2_decimal_places")


def _format_volume_to_decimal(volume):
    if isinstance(volume, str):
        volume_str = volume.strip().replace(',', '.')
        _check_volume_str_is_digit(volume_str)
    return Decimal(volume)


def _check_volume_str_is_digit(volume_str):
    if not volume_str.replace('.', '').isdigit():
        raise ValueError("volume_must_be_digit")