##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2017 Université catholique de Louvain (http://www.uclouvain.be)
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
from django import forms
from django.conf.urls import url
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from io import StringIO

from internship.models import *
from internship.utils import student_loader
from internship.utils.import_students import import_csv
from osis_common.models.serializable_model import SerializableModelAdmin


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


class StudentImportActionForm(forms.Form):
    file_upload = forms.FileField()


@admin.register(cohort.Cohort)
class CohortAdmin(SerializableModelAdmin):
    list_display = ('id', 'name', 'description', 'publication_start_date', 'subscription_start_date', 'subscription_end_date', 'free_internships_number', 'cohort_actions')
    readonly_fields = ('id', 'cohort_actions')
    fields = ('id', 'name', 'description', 'publication_start_date', 'subscription_start_date', 'subscription_end_date', 'free_internships_number', 'cohort_actions')

    def process_import(self, request, cohort_id):

        current_cohort = self.get_object(request, cohort_id)

        if request.method != 'POST':
            form = StudentImportActionForm()
        else:
            form = StudentImportActionForm(request.POST, request.FILES)
            if form.is_valid():
                file_upload = form.cleaned_data['file_upload']
                try:
                    with StringIO(file_upload.read().decode('utf-8')) as str_io:
                        result = import_csv(current_cohort, str_io)
                    self.message_user(request, _('Success'))
                except student_loader.BadCSVFormat as ex:
                    self.message_user(request, _('Unable to import the CSV file'))

                current_url = reverse(
                    'admin:internship_cohort_change',
                    args=[current_cohort.pk],
                    current_app=self.admin_site.name
                )

                return HttpResponseRedirect(current_url)

        context = self.admin_site.each_context(request)

        context.update({
            'form': form,
            'opts': self.model._meta,
        })

        return TemplateResponse(request,
                                'admin/internship/cohort/import_students.html',
                                context)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            url(r'^(?P<cohort_id>.+)/import_students/$',
                self.admin_site.admin_view(self.process_import),
                name='cohort-import-students'),
        ]
        return custom_urls + urls

    def cohort_actions(self, obj):
        return format_html(
            '<a class="button" href="{}">{}</a>',
            reverse('admin:cohort-import-students', args=[obj.pk]),
            _("Import Students")
        )

    cohort_actions.short_description = 'Actions'
    cohort_actions.allow_tags = True
