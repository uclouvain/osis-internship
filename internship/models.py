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
from django.db import models
from core.models import Organization, LearningUnitEnrollment, Student
from django.utils.translation import ugettext_lazy as _


class InternshipEnrollment(models.Model):
    external_id              = models.CharField(max_length = 100, blank = True, null = True)
    learning_unit_enrollment = models.ForeignKey(LearningUnitEnrollment)
    organization             = models.ForeignKey(Organization)
    start_date               = models.DateField()
    end_date                 = models.DateField()


class Place(models.Model):
    number                  = models.IntegerField()
    name                    = models.CharField(max_length = 100)
    address                 = models.CharField(max_length = 100)
    postal_code             = models.IntegerField()
    town                    = models.CharField(max_length = 100)
    country                 = models.CharField(max_length = 100)
    url                     = models.TextField(blank = True, null = True)
    #external_id intership master

class Student_(models.Model):
    student                  = models.ForeignKey(Student)
    noma                    = models.IntegerField()
    annual_bloc             = models.IntegerField()
    #external id periode                 =
    mail                    = models.CharField(max_length = 100)
    address                 = models.CharField(max_length = 100)
    postal_code             = models.IntegerField()
    town                    = models.CharField(max_length = 100)
    phone_number            = models.IntegerField()

class Internship(models.Model):
    name                    = models.CharField(max_length = 100)
    speciality              = models.CharField(max_length = 100)
    #external id    place
    student_min             = models.IntegerField()
    student_max             = models.IntegerField()

class Periode(models.Model):
    name                    = models.CharField(max_length = 100)
    date_start              = models.DateField()
    date_end                = models.DateField()

class InternshipMaster(models.Model):
    CIVILITY_CHOICE = (('Pr',_('Professor')), ('Dr',_('Doctor')), ('--',_('--')))
    TYPE_CHOICE = (('Sp',_('Specialiste')), ('Ge',_('Generalist')), ('--',_('--')))
    SPEC_CHOICE = (('MI',_('Medecine Interne')), ('CH',_('Chirurgie')), ('GO',_('Gynéco-Obsétrique')), ('PE',_('Pédiatrie')), ('UR',_('Urgence')), ('GE',_('Gériatrie')), ('--',_('--')))

    number                  = models.IntegerField()
    civility                = models.CharField(max_length = 2, blank = True, null = True, choices = CIVILITY_CHOICE, default = '--')
    type                    = models.CharField(max_length = 2, blank = True, null = True, choices = TYPE_CHOICE, default = '--')
    speciality_id           = models.CharField(max_length = 2, blank = True, null = True, choices = SPEC_CHOICE, default = '--')
    speciality              = models.CharField(max_length = 100,blank = True, null = True)
    mail                    = models.CharField(max_length = 100,blank = True, null = True)
    #external_id places
