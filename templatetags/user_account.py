##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2022 Université catholique de Louvain (http://www.uclouvain.be)
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

from datetime import date

from django.template.defaulttags import register
from django.utils.translation import gettext as _

from internship.models.enums.user_account_expiry import UserAccountExpiryLevel


@register.inclusion_tag('internship/tags/user_account_expiry.html')
def user_account_expiry(expiry_date):
    if expiry_date:
        delta = expiry_date - date.today()
        if delta.days <= 0:
            remaining = _('Expired')
            level = UserAccountExpiryLevel.DANGER.value
        elif delta.days <= 7:
            remaining = _('{} day(s)').format(delta.days)
            level = UserAccountExpiryLevel.DANGER.value
        elif delta.days < 30:
            remaining = _('< 1 month')
            level = UserAccountExpiryLevel.WARNING.value
        elif delta.days <= 90:
            remaining = _('< 3 months')
            level = UserAccountExpiryLevel.WARNING.value
        else:
            remaining = _('> 3 months')
            level = UserAccountExpiryLevel.OK.value
        return {
            'remaining': remaining,
            'level': level,
            'expiry_date': expiry_date
        }
    return {'expiry_date': expiry_date}
