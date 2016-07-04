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
    def find_interships_by_learning_unit_organization(speciality, organization):
        internships = InternshipOffer.objects.filter(speciality__name=speciality)\
                                            .filter(organization__reference=organization)
        return internships

    @staticmethod
    def find_interships_by_learning_unit(speciality):
        internships = InternshipOffer.objects.filter(speciality__name=speciality)
        return internships

    @staticmethod
    def find_interships_by_organization(organization):
        internships = InternshipOffer.objects.filter(organization__name=organization)
        return internships

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
    def find_masters_by_speciality_and_organization(speciality, organization):
        masters = InternshipMaster.objects.filter(speciality=speciality)\
                                            .filter(organization__reference=organization)
        return masters

    @staticmethod
    def find_masters_by_speciality(speciality):
        masters = InternshipMaster.objects.filter(speciality=speciality)
        return masters

    @staticmethod
    def find_masters_by_organization(organization):
        masters = InternshipMaster.objects.filter(organization__name=organization)
        return masters

    @staticmethod
    def find_master_by_firstname_name(firstname, name):
        master = InternshipMaster.objects.filter(first_name=firstname)\
                                            .filter(last_name=name)
        return master


class InternshipChoice(models.Model):
    student             = models.ForeignKey('base.Student')
    organization        = models.ForeignKey('internship.Organization')
    speciality          = models.ForeignKey('internship.InternshipSpeciality',null=True)
    choice              = models.IntegerField()
    priority            = models.BooleanField()

    @staticmethod
    def find_by_all_student():
        all = InternshipChoice.objects.all()
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
    def find_by(s_organization=None, s_speciality=None, s_organization_ref=None, s_choice=None,
                s_define_choice=None, s_student=None):

        has_criteria = False
        queryset = InternshipChoice.objects

        if s_organization:
            queryset = queryset.filter(organization=s_organization)
            has_criteria = True

        if s_speciality:
            queryset = queryset.filter(speciality=s_speciality)
            has_criteria = True

        if s_organization_ref:
            queryset = queryset.filter(organization__reference=s_organization_ref).order_by('choice')
            has_criteria = True

        if s_define_choice:
            queryset = queryset.filter(choice=s_define_choice)
            has_criteria = True

        if s_choice:
            if s_choice == 1 :
                queryset = queryset.filter(choice=s_choice)
            else :
                queryset = queryset.exclude(choice=1)
            has_criteria = True

        if s_student:
            queryset = queryset.filter(student = s_student).order_by('choice')
            has_criteria = True

        if has_criteria:
            return queryset
        else:
            return None

class Period(models.Model):
    name = models.CharField(max_length=255)
    date_start = models.DateField(blank=False)
    date_end = models.DateField(blank=False)

    def find_all():
        return Period.objects.all()

    @staticmethod
    def find_by(name=None):
        queryset = Period.objects

        if name:
            queryset = queryset.filter(name=name)
            has_criteria = True

        if has_criteria:
            return queryset
        else:
            return None

    @staticmethod
    def find_by(name=None):
        queryset = Period.objects

        if name:
            queryset = queryset.filter(name=name)
            has_criteria = True

        if has_criteria:
            return queryset
        else:
            return None

class PeriodInternshipPlaces(models.Model):
    period = models.ForeignKey('internship.Period')
    internship = models.ForeignKey('internship.InternshipOffer')
    number_places = models.IntegerField(blank=None, null=False)

    @staticmethod
    def find_by(period=None, internship=None, relation_id=None):
        queryset = PeriodInternshipPlaces.objects

        if period:
            queryset = queryset.filter(period=period)
            has_criteria = True

        if internship:
            queryset = queryset.filter(internship=internship)
            has_criteria = True

        if relation_id:
            queryset = queryset.get(pk=relation_id)
            has_criteria = True

        if has_criteria:
            return queryset
        else:
            return None

class InternshipSpeciality(models.Model):
    learning_unit = models.ForeignKey('base.LearningUnit')
    name = models.CharField(max_length=125, blank=False, null=False)
    mandatory = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    @staticmethod
    def find_by(learning_unit=None, name=None):
        queryset = InternshipSpeciality.objects

        if learning_unit:
            queryset = queryset.filter(learning_unit=learning_unit)
            has_criteria = True

        if name:
            queryset = queryset.filter(name=name)
            has_criteria = True

        if has_criteria:
            return queryset
        else:
            return None

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
    def find_by_id(organization_id):
        return Organization.objects.get(pk=organization_id)

    @staticmethod
    def search(acronym=None, name=None, reference=None):
        has_criteria = False
        queryset = Organization.objects

        if acronym:
            queryset = queryset.filter(acronym=acronym)
            has_criteria = True

        if name:
            queryset = queryset.filter(name=name)
            has_criteria = True

        if reference:
            queryset = queryset.filter(reference=reference)
            has_criteria = True

        if has_criteria:
            return queryset
        else:
            return None

    @staticmethod
    def find_all_order_by_reference():
        return Organization.objects.all().order_by('reference')


    @staticmethod
    def find_by_type(type=None, order_by=None):
        if order_by:
            queryset = Organization.objects.filter(type=type).order_by(*order_by)
        else:
            queryset = Organization.objects.filter(type=type)

        return queryset


class OrganizationAddress(models.Model):
    organization = models.ForeignKey('Organization')
    label = models.CharField(max_length=20)
    location = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=20)
    city = models.CharField(max_length=255)
    country = models.CharField(max_length=255)

    @staticmethod
    def find_by_organization(organization):
        return OrganizationAddress.objects.filter(organization=organization).order_by('label')


    @staticmethod
    def find_by_id(organization_address_id):
        return OrganizationAddress.objects.get(pk=organization_address_id)


class InternshipStudentInformation(models.Model):
    person = models.ForeignKey('base.Person')
    location = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=20)
    city = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, blank=True, null=True)
    phone_mobile = models.CharField(max_length=100, blank=True, null=True)

    @staticmethod
    def find_by_person(person):
        return InternshipStudentInformation.objects.get(person=person)
