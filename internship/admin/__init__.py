from internship.models import *
from django.contrib import admin

admin.site.register(internship_offer.InternshipOffer,
                    internship_offer.InternshipOfferAdmin)

admin.site.register(internship_enrollment.InternshipEnrollment,
                    internship_enrollment.InternshipEnrollmentAdmin)

admin.site.register(internship_master.InternshipMaster,
                    internship_master.InternshipMasterAdmin)

admin.site.register(internship_choice.InternshipChoice,
                    internship_choice.InternshipChoiceAdmin)

admin.site.register(period.Period,
                    period.PeriodAdmin)

admin.site.register(period_internship_places.PeriodInternshipPlaces,
                    period_internship_places.PeriodInternshipPlacesAdmin)

admin.site.register(internship_speciality.InternshipSpeciality,
                    internship_speciality.InternshipSpecialityAdmin)

admin.site.register(organization.Organization,
                    organization.OrganizationAdmin)

admin.site.register(organization_address.OrganizationAddress,
                    organization_address.OrganizationAddressAdmin)

admin.site.register(internship_student_information.InternshipStudentInformation,
                    internship_student_information.InternshipStudentInformationAdmin)

admin.site.register(internship_student_affectation_stat.InternshipStudentAffectationStat,
                    internship_student_affectation_stat.InternshipStudentAffectationStatAdmin)

admin.site.register(affectation_generation_time.AffectationGenerationTime,
                    affectation_generation_time.AffectationGenerationTimeAdmin)

admin.site.register(internship_speciality_group.InternshipSpecialityGroup,
                    internship_speciality_group.InternshipSpecialityGroupAdmin)

admin.site.register(internship_speciality_group_member.InternshipSpecialityGroupMember,
                    internship_speciality_group_member.InternshipSpecialityGroupMemberAdmin)



from .cohort import CohortAdmin