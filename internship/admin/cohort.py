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
from io import StringIO

from django import forms
from django.conf.urls import url
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from internship.models.cohort import Cohort
from internship.utils.student_loader import load_internship_students


class StudentImportActionForm(forms.Form):
    file_upload = forms.FileField()


@admin.register(Cohort)
class CohortAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'cohort_actions')
    readonly_fields = ('id', 'name', 'description', 'cohort_actions')

    def process_import(self, request, cohort_id):

        current_cohort = self.get_object(request, cohort_id)

        if request.method != 'POST':
            form = StudentImportActionForm()
        else:
            form = StudentImportActionForm(request.POST, request.FILES)
            if form.is_valid():
                file_upload = form.cleaned_data['file_upload']

                with StringIO(file_upload.read().decode('utf-8')) as strIO:
                    result = load_internship_students(strIO)

                self.message_user(request, _('Success'))

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
