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
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.translation import ugettext_lazy as _


class InternshipOffer(models.Model):
    organization        = models.ForeignKey('internship.Organization')
    speciality          = models.ForeignKey('internship.InternshipSpeciality',null=True)
    title = models.CharField(max_length=255)
    maximum_enrollments = models.IntegerField()
    selectable          = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    @staticmethod
    def find_internships():
        return InternshipOffer.objects.all().order_by('speciality__name', 'organization__reference')

    @staticmethod
    def search(**kwargs):
        kwargs = {k: v for k, v in kwargs.items() if v}
        queryset = InternshipOffer.objects.filter(**kwargs)
        return queryset

    @staticmethod
    def find_intership_by_id(id):
        internship = InternshipOffer.objects.all()
        for i in internship:
            if int(i.id) == int(id):
                return i

        internship = InternshipChoice.objects.all()
        for i in internship:
            if int(i.id) == int(id):
                return i

    class Meta:
        permissions = (
            ("is_internship_manager", "Is Internship Manager"),
            ("can_access_internship","Can access internships"),
        )


class InternshipEnrollment(models.Model):
    student = models.ForeignKey('base.student')
    internship_offer = models.ForeignKey(InternshipOffer)
    place = models.ForeignKey('internship.Organization')
    period = models.ForeignKey('internship.Period')

    def __str__(self):
        return u"%s" % self.learning_unit_enrollment.student

    @staticmethod
    def search(**kwargs):
        kwargs = {k: v for k, v in kwargs.items() if v}
        queryset = InternshipEnrollment.objects.filter(**kwargs)
        return queryset


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

    organization     = models.ForeignKey('internship.Organization', null=True)
    #internship_offer = models.ForeignKey(InternshipOffer)
    first_name = models.CharField(max_length=50, blank=True, null=True, db_index=True)
    last_name = models.CharField(max_length=50, blank=True, null=True, db_index=True)
    reference = models.CharField(max_length=50, blank=True, null=True)
    civility = models.CharField(max_length=50, blank=True, null=True)
    type_mastery = models.CharField(max_length=50, blank=True, null=True)
    speciality = models.CharField(max_length=50, blank=True, null=True)

    @staticmethod
    def find_masters():
        return InternshipMaster.objects.all()

    def __str__(self):
        return u"%s" % (self.reference)

    @staticmethod
    def search(**kwargs):
        kwargs = {k: v for k, v in kwargs.items() if v}
        queryset = InternshipMaster.objects.filter(**kwargs)
        return queryset


class InternshipChoice(models.Model):
    student             = models.ForeignKey('base.Student')
    organization        = models.ForeignKey('internship.Organization')
    speciality          = models.ForeignKey('internship.InternshipSpeciality',null=True)
    choice              = models.IntegerField()
    priority            = models.BooleanField()

    @staticmethod
    def find_by_all_student():
        all = InternshipChoice.objects.all().order_by('student__person__last_name')
        students_list=[]
        for a in all:
            students_list.append(a.student)
        unique = []
        [unique.append(item) for item in students_list if item not in unique]
        return unique

    @staticmethod
    def find_by_student(s_student):
        internships = InternshipChoice.objects.filter(student = s_student).order_by('choice')
        return internships

    @staticmethod
    def find_by_student_desc(s_student):
        internships = InternshipChoice.objects.filter(student = s_student).order_by('-choice')
        return internships

    @staticmethod
    def search(**kwargs):
        kwargs = {k: v for k, v in kwargs.items() if v}
        queryset = InternshipChoice.objects.filter(**kwargs)
        return queryset

    @staticmethod
    def search_other_choices(**kwargs):
        kwargs = {k: v for k, v in kwargs.items() if v}
        queryset = InternshipChoice.objects.filter(**kwargs)
        queryset = queryset.exclude(choice=1)
        return queryset

class Period(models.Model):
    name = models.CharField(max_length=255)
    date_start = models.DateField(blank=False)
    date_end = models.DateField(blank=False)

    def __str__(self):
        return u"%s" % (self.name)

    @staticmethod
    def search(**kwargs):
        kwargs = {k: v for k, v in kwargs.items() if v}
        queryset = Period.objects.filter(**kwargs)
        return queryset

class PeriodInternshipPlaces(models.Model):
    period = models.ForeignKey('internship.Period')
    internship = models.ForeignKey('internship.InternshipOffer')
    number_places = models.IntegerField(blank=None, null=False)

    @staticmethod
    def search(**kwargs):
        kwargs = {k: v for k, v in kwargs.items() if v}
        queryset = PeriodInternshipPlaces.objects.filter(**kwargs)
        return queryset

class InternshipSpeciality(models.Model):
    learning_unit = models.ForeignKey('base.LearningUnit')
    name = models.CharField(max_length=125, blank=False, null=False)
    mandatory = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    @staticmethod
    def search(**kwargs):
        kwargs = {k: v for k, v in kwargs.items() if v}
        queryset = InternshipSpeciality.objects.filter(**kwargs)
        return queryset

    @staticmethod
    def find_all():
        return InternshipSpeciality.objects.all().order_by('name')


class Organization(models.Model):
    name = models.CharField(max_length=255)
    acronym = models.CharField(max_length=15)
    website = models.URLField(max_length=255, blank=True, null=True)
    reference = models.CharField(max_length=30, blank=True, null=True)
    type = models.CharField(max_length=30, blank=True, null=True)

    def __str__(self):
        return self.name

    @staticmethod
    def search(**kwargs):
        kwargs = {k: v for k, v in kwargs.items() if v}
        queryset = Organization.objects.filter(**kwargs)
        return queryset

class OrganizationAddress(models.Model):
    organization = models.ForeignKey('Organization')
    label = models.CharField(max_length=20)
    location = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=20)
    city = models.CharField(max_length=255)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    country = models.CharField(max_length=255)

    @staticmethod
    def search(**kwargs):
        kwargs = {k: v for k, v in kwargs.items() if v}
        queryset = OrganizationAddress.objects.filter(**kwargs)
        return queryset


class InternshipStudentInformation(models.Model):
    person = models.ForeignKey('base.Person')
    location = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=20)
    city = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    phone_mobile = models.CharField(max_length=100, blank=True, null=True)

    @staticmethod
    def search(**kwargs):
        kwargs = {k: v for k, v in kwargs.items() if v}
        queryset = InternshipStudentInformation.objects.filter(**kwargs)
        return queryset

    @staticmethod
    def find_all():
        return InternshipStudentInformation.objects.all().order_by('person__last_name', 'person__first_name')

class InternshipStudentAffectationStat(models.Model):
    student = models.ForeignKey('base.Student')
    organization = models.ForeignKey('internship.Organization')
    speciality = models.ForeignKey('internship.InternshipSpeciality')
    period = models.ForeignKey('internship.Period')
    choice = models.IntegerField(blank=False, null=False)
    cost = models.IntegerField(blank=False, null=False)
    consecutive_month = models.BooleanField(default=False, null=False)
    type_of_internship = models.CharField(max_length=1, blank=False, null=False, default='N')

    @staticmethod
    def search(**kwargs):
        kwargs = {k: v for k, v in kwargs.items() if v}
        queryset = InternshipStudentAffectationStat.objects.filter(**kwargs)
        return queryset
