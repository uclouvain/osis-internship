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
from django.core.validators import MaxValueValidator, MinValueValidator


class AcademicAssistant(models.Model):
    PHD_INSCRIPTION_CHOICES = (
        ('Y', _('Yes')),
        ('N', _('No')),
        ('P', _('In progress')))
    
    person                  = models.ForeignKey('base.Person')
    position_id             = models.CharField(max_length=12)
    eft                     = models.DecimalField(max_digits=3, decimal_places=2)
    sap_id                  = models.CharField(max_length=12)
    entry_date              = models.DateField()
    end_date                = models.DateField()
    scale                   = models.CharField(maxlength=3)
    thesis_title            = models.CharField(maxlength=255, null=True, blank=True)
    phd_inscription_date    = models.DateField(null=True, blank=True)
    confirmation_test_date  = models.DateField(null=True, blank=True)
    thesis_date             = models.DateField(null=True, blank=True)
    expected_phd_date       = models.DateField(null=True, blank=True)
    supervisor_email        = models.CharField(maxlength=255, null=True, blank=True)
    remark                  = models.TextField(null=True, blank=True)
    inscription             = models.CharField(max_length=1, choices=PHD_INSCRIPTION_CHOICES, default='Y')
    

class AssistantMandate(models.Model):
    
    RENEWAL_TYPE_CHOICES = (
        ('N', _('Normal')),
        ('E', _('Exceptional')))
    
    STATE_CHOICES = (
        ('0', _('To do')),
        ('1', _('Trts')),
        ('2', _('PhD supervisor')),
        ('3', _('Research')),
        ('4', _('Supervision')),
        ('5', _('Vice rector')))
    
    APPEAL_CHOICES = (
        ('0', _('N/A')),
        ('1', _('Positive appeal')),
        ('2', _('Negative appeal')),
        ('3', _('Appeal in progress')),
        ('4', _('No appeal')))
    
    assistant                       = models.ForeignKey(AcademicAssistant)
    absences                        = models.TextField(null=True, blank=True)
    comment                         = models.TextField(null=True, blank=True)
    other_status                    = models.CharField(maxlength=50, null=True, blank=True)
    renewal_type                    = models.CharField(max_length=1, choices=RENEWAL_TYPE_CHOICES, default='N')
    external_functions              = models.TextField(null=True, blank=True)
    external_contract               = models.CharField(maxlength=255, null=True, blank=True)
    justification                   = models.TextField(null=True, blank=True)
    state                           = models.CharField(max_length=1, choices=STATE_CHOICES, default='0')
    tutoring_remark                 = models.TextField(null=True, blank=True)
    activities_report_remark        = models.TextField(null=True, blank=True)
    research_percent                = models.PositiveIntegerField(validators=[MinValueValidator(0),MaxValueValidator(100)], default=0)
    tutoring_percent                = models.PositiveIntegerField(validators=[MinValueValidator(0),MaxValueValidator(100)], default=0)
    service_activities_percent      = models.PositiveIntegerField(validators=[MinValueValidator(0),MaxValueValidator(100)], default=0)
    formation_activities_percent    = models.PositiveIntegerField(validators=[MinValueValidator(0),MaxValueValidator(100)], default=0)
    internships                     = models.TextField(null=True, blank=True)
    conferences                     = models.TextField(null=True, blank=True)
    publications                    = models.TextField(null=True, blank=True)
    awards                          = models.TextField(null=True, blank=True)
    framing                         = models.TextField(null=True, blank=True)
    remark                          = models.TextField(null=True, blank=True)
    degrees                         = models.TextField(null=True, blank=True)
    formations                      = models.TextField(null=True, blank=True)
    faculty_representation          = models.PositiveIntegerField(default=0)
    institute_representation        = models.PositiveIntegerField(default=0)
    sector_representation           = models.PositiveIntegerField(default=0)
    governing_body_representation   = models.PositiveIntegerField(default=0)
    corsci_representation           = models.PositiveIntegerField(default=0)
    students_service                = models.PositiveIntegerField(default=0)
    infrastructure_mgmt_service     = models.PositiveIntegerField(default=0)
    events_organisation_service     = models.PositiveIntegerField(default=0)
    publishing_field_service        = models.PositiveIntegerField(default=0)
    scientific_jury_service         = models.PositiveIntegerField(default=0)
    appeal                          = models.CharField(max_length=1, choices=APPEAL_CHOICES, default='0')
    special                         = models.BooleanField(default=False)
    contract_duration               = models.CharField(maxlength=30) 
    contract_duration_fte           = models.CharField(maxlength=30)
    
class AssistantDocument(models.Model):
    
    DOC_TYPE_CHOICES = (
        ('0', _('PhD')),
        ('1', _('Tutoring')),
        ('2', _('Research'))
        )
    
    assistant = models.ForeignKey(AcademicAssistant)
    mandate = models.ForeignKey(AssistantMandate)
    doc_type = models.CharField(max_length=1, choices=DOC_TYPE_CHOICES)
    
class TutoringLearningUnitYear(models.Model):
    
    mandate                     = models.ForeignKey(AssistantMandate)
    sessions_duration           = models.PositiveIntegerField(null=True, blank=True)
    sessions_number             = models.PositiveIntegerField(null=True, blank=True)
    series_number               = models.PositiveIntegerField(null=True, blank=True)
    face_to_face_duration       = models.PositiveIntegerField(null=True, blank=True)
    attendees                   = models.PositiveIntegerField(null=True, blank=True)
    preparation_duration        = models.PositiveIntegerField(null=True, blank=True)
    exams_supervision_duration  = models.PositiveIntegerField(null=True, blank=True)
    
class Review(models.Model):
    
    ADVICE_CHOICES = (
        ('0', _('Favorable')),
        ('1', _('Conditional')),
        ('2', _('Unfavourable'))
        )
    
    mandate         = models.ForeignKey(AssistantMandate)
    advice          = models.CharField(max_length=1, choices=ADVICE_CHOICES, default='0')
    justification   = models.TextField(null=True, blank=True)
    remark          = models.TextField(null=True, blank=True)
    confidential    = models.TextField(null=True, blank=True)
    

    
    
    

    
    
