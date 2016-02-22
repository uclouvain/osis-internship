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
from django import template
from base.models import OfferYear

register = template.Library()

@register.assignment_tag(takes_context=True)
def full_width(context):

    offer_year = context['offer_year']
    if (not offer_year.orientation_sibling is None and len(list(offer_year.orientation_sibling))>0)  and ((not offer_year.offer_year_children is None and len(list(offer_year.offer_year_children))>0)  or (not offer_year.offer_year_sibling is None and len(list(offer_year.offer_year_sibling))>0 )):
        return False

    return True
