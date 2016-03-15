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
from django.utils.translation import ugettext_lazy as _



class InternshipOffer(models.Model):
    organization        = models.ForeignKey('base.Organization')
    learning_unit_year  = models.ForeignKey('base.LearningUnitYear')
    title               = models.CharField(max_length=255)
    maximum_enrollments = models.IntegerField()

    def __str__(self):
        return self.title

    @staticmethod
    def find_internships():
        return InternshipOffer.objects.all()

    @staticmethod
    def find_internships_by_luy_and_place(luy, place):
        query = InternshipOffer.objects.all()
        internships_found=[]
        for i in query :
            if i.learning_unit_year.title==luy and i.organization.name == place:
                internships_found.append(i)

        return internships_found

    @staticmethod
    def find_internships_by_luy(luy):
        query = InternshipOffer.objects.all()
        internships_found=[]
        for i in query :
            if i.learning_unit_year.title==luy:
                internships_found.append(i)

        return internships_found

    @staticmethod
    def find_internships_by_place(place):
        query = InternshipOffer.objects.all()
        internships_found=[]
        for i in query :
            if i.organization.name == place:
                internships_found.append(i)

        return internships_found


class InternshipEnrollment(models.Model):
    learning_unit_enrollment = models.ForeignKey('base.LearningUnitEnrollment')
    internship_offer         = models.ForeignKey(InternshipOffer)
    start_date               = models.DateField()
    end_date                 = models.DateField()

    def __str__(self):
        return u"%s" % self.learning_unit_enrollment.student


class InternshipMaster(models.Model):
    CIVILITY_CHOICE = (('PROFESSOR',_('Professor')),
                       ('DOCTOR',_('Doctor')))
    TYPE_CHOICE = (('SPECIALIST',_('Specialist')),
                   ('GENERALIST',_('Generalist')))
    SPECIALITY_CHOICE = (('INTERNAL_MEDICINE',_('Internal Medicine')),
                        ('SURGERY',_('Surgery')),
                        ('GYNEC_OBSTETRICS',_('Gynec-Obstetrics')),
                        ('PEDIATRICS',_('Pediatrics')),
                        ('EMERGENCY',_('Emergency')),
                        ('GERIATRICS',_('Geriatrics')))

    organization     = models.ForeignKey('base.Organization')
    internship_offer = models.ForeignKey(InternshipOffer)
    person           = models.ForeignKey('base.Person')
    reference        = models.CharField(max_length=30, blank=True, null=True)
    civility         = models.CharField(max_length=20, blank=True, null=True, choices=CIVILITY_CHOICE)
    type_mastery     = models.CharField(max_length=20, blank=True, null=True, choices=TYPE_CHOICE)
    speciality       = models.CharField(max_length=20, blank=True, null=True, choices=SPECIALITY_CHOICE)

    @staticmethod
    def find_masters():
        return InternshipMaster.objects.all()

    def __str__(self):
        return u"%s - %s" % (self.person, self.reference)

    @staticmethod
    def find_masters_by_spec_and_place(spec, place):
        query = InternshipMaster.objects.all()
        masters_found=[]
        for m in query :
            if m.speciality==spec and m.organization.name == place:
                masters_found.append(m)

        return masters_found

    @staticmethod
    def find_masters_by_spec(spec):
        query = InternshipMaster.objects.all()
        masters_found=[]
        for m in query :
            if m.speciality==spec:
                masters_found.append(m)

        return masters_found

    @staticmethod
    def find_masters_by_place(place):
        query = InternshipMaster.objects.all()
        masters_found=[]
        for m in query :
            if m.organization.name == place:
                masters_found.append(m)

        return masters_found
