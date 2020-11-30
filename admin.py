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
from django.contrib import admin

from internship.models import *
from internship.models import internship_score_reason

admin.site.register(cohort.Cohort, cohort.CohortAdmin)

admin.site.register(internship.Internship, internship.InternshipAdmin)

admin.site.register(internship_offer.InternshipOffer, internship_offer.InternshipOfferAdmin)

admin.site.register(internship_enrollment.InternshipEnrollment, internship_enrollment.InternshipEnrollmentAdmin)

admin.site.register(internship_master.InternshipMaster, internship_master.InternshipMasterAdmin)

admin.site.register(master_allocation.MasterAllocation, master_allocation.MasterAllocationAdmin)

admin.site.register(internship_choice.InternshipChoice, internship_choice.InternshipChoiceAdmin)

admin.site.register(period.Period, period.PeriodAdmin)

admin.site.register(internship_speciality.InternshipSpeciality, internship_speciality.InternshipSpecialityAdmin)

admin.site.register(organization.Organization, organization.OrganizationAdmin)

admin.site.register(internship_student_information.InternshipStudentInformation,
                    internship_student_information.InternshipStudentInformationAdmin)

admin.site.register(period_internship_places.PeriodInternshipPlaces,
                    period_internship_places.PeriodInternshipPlacesAdmin)

admin.site.register(internship_student_affectation_stat.InternshipStudentAffectationStat,
                    internship_student_affectation_stat.InternshipStudentAffectationStatAdmin)

admin.site.register(affectation_generation_time.AffectationGenerationTime,
                    affectation_generation_time.AffectationGenerationTimeAdmin)

admin.site.register(internship_score.InternshipScore,
                    internship_score.InternshipScoreAdmin)

admin.site.register(internship_score_mapping.InternshipScoreMapping,
                    internship_score_mapping.InternshipScoreMappingAdmin)

admin.site.register(internship_score_reason.InternshipScoreReason,
                    internship_score_reason.InternshipScoreReasonAdmin)
