##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2024 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.db import models

from osis_common.models.serializable_model import SerializableModelAdmin, SerializableModel

from django.utils.translation import gettext_lazy as _

APDS_DESCRIPTIONS = {
    "1": _("Take a history (anamnesis)"),
    "2": _("Conduct clinical examination"),
    "3": _("Appreciate medical emergency"),
    "4": _("Establish a diagnosis"),
    "5": _("Complement patient record"),
    "6": _("Oral presentation of a clinical situation"),
    "7": _("Select diagnostic tests"),
    "8": _("Write medical prescriptions"),
    "9": _("Perform technical procedures"),
    "10": _("Formulate clinical questions"),
    "11": _("Communicate (broad sense)"),
    "12": _("Work as a team"),
    "13": _("Make/receive transmission report"),
    "14": _("Obtain informed consent"),
    "15": _("Contribute to quality of care and patient safety"),
}

class InternshipModalityApdAdmin(SerializableModelAdmin):
    list_display = ('internship', 'apd')


class InternshipModalityApd(SerializableModel):
    internship = models.ForeignKey('internship.Internship', on_delete=models.PROTECT)
    apd = models.IntegerField()
