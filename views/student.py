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
import json
from io import BytesIO

from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.http import require_POST
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.translation import ugettext_lazy as _

from reference.models import country
from base import models as mdl
from internship import models as mdl_int
from internship.forms.form_student_information import StudentInformationForm
from internship.forms.students_import_form import StudentsImportActionForm
from internship.utils.importing.import_students import import_xlsx


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def internships_student_resume(request, cohort_id):
    cohort = get_object_or_404(mdl_int.cohort.Cohort, pk=cohort_id)
    students_with_status = _get_students_with_status(cohort)
    student_with_internships = mdl_int.internship_choice.get_number_students(cohort)
    students_can_have_internships = mdl_int.internship_student_information.get_number_students(cohort)
    student_without_internship = students_can_have_internships - student_with_internships
    number_students_ok = len([x for x in students_with_status if x[1]])
    number_students_not_ok = len([x for x in students_with_status if x[1] is False])
    number_generalists = mdl_int.internship_student_information.get_number_of_generalists(cohort)
    number_specialists = students_can_have_internships - number_generalists
    context = {
        'search_name': None,
        'search_firstname': None,
        'students': students_with_status,
        'students_ok': number_students_ok,
        'students_not_ok': number_students_not_ok,
        'student_with_internships': student_with_internships,
        'students_can_have_internships': students_can_have_internships,
        'student_without_internship': student_without_internship,
        "number_generalists": number_generalists,
        "number_specialists": number_specialists,
        'cohort': cohort,
    }
    return render(request, "students.html", context)


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def student_form(request, cohort_id):
    cohort = get_object_or_404(mdl_int.cohort.Cohort, pk=cohort_id)
    countries = country.find_all()
    return render(request, 'student_form.html', locals())


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def get_student(request):
    registration_id = request.GET.get('id', '')
    student = mdl.student.find_by_registration_id(registration_id)
    if student:
        cohort = request.GET.get('cohort', '')
        existing_student = mdl_int.internship_student_information.find_by_person(student.person, cohort)
        if not existing_student:
            data = {'id': student.person.id,
                    'first_name': student.person.first_name,
                    'last_name': student.person.last_name,
                    'gender': student.person.gender,
                    'email': student.person.email,
                    'phone_mobile': student.person.phone_mobile,
                    'birth_date': student.person.birth_date.strftime("%Y-%m-%d")}

            student_address = mdl.person_address.find_by_person(student.person)
            if student_address:
                address = student_address[0]
                data['location'] = address.location
                data['postal_code'] = address.postal_code
                data['city'] = address.city
                data['country'] = address.country.id
        else:
            data = {'error': str(_('student_already_exists'))}
    else:
        data = {'error': str(_('student_doesnot_exist'))}

    return HttpResponse(json.dumps(data), content_type='application/json')


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def student_save(request, cohort_id):
    cohort = get_object_or_404(mdl_int.cohort.Cohort, pk=cohort_id)
    student = mdl_int.internship_student_information.InternshipStudentInformation(cohort=cohort)

    form = StudentInformationForm(request.POST, instance=student)
    errors = []
    if form.is_valid():
        form.save()
    else:
        errors.append(form.errors)

    if errors:
        return HttpResponseRedirect(reverse("internship_student_form", args=[cohort_id]))

    return HttpResponseRedirect(reverse("internships_student_resume", args=[cohort_id]))


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def internships_student_read(request, cohort_id, student_id):
    cohort = get_object_or_404(mdl_int.cohort.Cohort, pk=cohort_id)
    student = mdl.student.find_by_id(student_id)

    if not request.user.has_perm('internship.is_internship_manager'):
        person_who_read = mdl.person.find_by_user(request.user)
        student_who_read = mdl.student.find_by_person(person_who_read)
        if not student_who_read or not student or student_who_read.pk != student.pk:
            raise PermissionDenied(request)

    if not student:
        return render(request, "student.html", {'errors': ['student_doesnot_exist']})

    information = mdl_int.internship_student_information.search(person=student.person).first()
    internship_choices = mdl_int.internship_choice.get_choices_made(cohort=cohort, student=student).order_by('choice')
    specialities = mdl_int.internship_speciality.search(mandatory=True, cohort=cohort)
    internships = mdl_int.internship.Internship.objects.filter(cohort=cohort, pk__gte=1)
    affectations = mdl_int.internship_student_affectation_stat.find_by_student(student, cohort).\
        order_by("period__date_start")
    periods = mdl_int.period.search(cohort=cohort).order_by("date_start")
    organizations = mdl_int.organization.search(cohort=cohort)

    return render(request, "student.html", locals())


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def internship_student_information_modification(request, cohort_id, student_id):
    cohort = get_object_or_404(mdl_int.cohort.Cohort, pk=cohort_id)
    student = mdl.student.find_by_id(student_id)
    information = mdl_int.internship_student_information.search(person=student.person, cohort=cohort).first()
    form = StudentInformationForm()
    return render(request, "student_information_modification.html", locals())


@login_required
@require_POST
@permission_required('internship.is_internship_manager', raise_exception=True)
def student_save_information_modification(request, cohort_id, student_id):
    cohort = get_object_or_404(mdl_int.cohort.Cohort, pk=cohort_id)
    student = mdl.student.find_by_id(student_id)
    informations = mdl_int.internship_student_information.find_by_person(student.person, cohort)
    if not informations:
        information = mdl_int.internship_student_information.InternshipStudentInformation()
        information.person = student.person
    else:
        information = informations.first()

    if information.cohort is None:
        information.cohort = cohort

    form = StudentInformationForm(request.POST, instance=information)
    if form.is_valid():
        information.email = form.cleaned_data.get('email')
        information.phone_mobile = form.cleaned_data.get('phone_mobile')
        information.location = form.cleaned_data.get('location')
        information.postal_code = form.cleaned_data.get('postal_code')
        information.city = form.cleaned_data.get('city')
        information.country = form.cleaned_data.get('country')
        information.contest = form.cleaned_data.get('contest')
        information.save()

    redirect_url = reverse('internships_student_read', args=[cohort_id, student_id])
    return HttpResponseRedirect(redirect_url)


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def internship_student_affectation_modification(request, cohort_id, student_id):
    cohort = get_object_or_404(mdl_int.cohort.Cohort, pk=cohort_id)
    internship_choice = mdl_int.internship_choice.search(student__pk=student_id)
    if not internship_choice:
        student = mdl.student.find_by_id(student_id)
        information = mdl_int.internship_choice.InternshipChoice()
        information.student = student
    else:
        information = internship_choice.first()
    organizations = mdl_int.organization.search(cohort=cohort)
    organizations = mdl_int.organization.sort_organizations(organizations)

    specialities = mdl_int.internship_speciality.find_all(cohort=cohort)
    for speciality in specialities:
        number = [int(s) for s in speciality.name.split() if s.isdigit()]
        if number:
            speciality.acronym = speciality.acronym + " " + str(number[0])
    periods = mdl_int.period.search(cohort=cohort)

    affectations = mdl_int.internship_student_affectation_stat.search(student__pk=student_id)
    internships = {}
    for period in periods:
        affectation = _get_affectation_for_period(affectations, period)
        if affectation and affectation.internship:
            internships[period.id] = affectation.internship.id

    return render(request, "student_affectation_modification.html", locals())


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def student_save_affectation_modification(request, cohort_id, student_id):
    cohort = get_object_or_404(mdl_int.cohort.Cohort, pk=cohort_id)
    student = mdl.student.find_by_id(student_id)

    periods = []
    if 'period' in request.POST:
        periods = request.POST.getlist('period')

    organizations = []
    if 'organization' in request.POST:
        organizations = request.POST.getlist('organization')

    specialties = []
    if 'specialty' in request.POST:
        specialties = request.POST.getlist('specialty')

    internships = []
    if 'internship' in request.POST:
        internships = request.POST.getlist('internship')

    check_error_present = False
    num_periods = len(periods)
    for num_period in range(0, num_periods):
        if organizations[num_period]:
            organization = mdl_int.organization.search(cohort=cohort, reference=organizations[num_period])[0]
            specialty = mdl_int.internship_speciality.search(cohort=cohort, name=specialties[num_period])[0]
            period = mdl_int.period.search(cohort=cohort, name=periods[num_period])[0]
            check_internship_present = mdl_int.internship_offer.search(cohort=cohort,
                                                                       organization=organization,
                                                                       speciality=specialty)
            if len(check_internship_present) == 0:
                check_error_present = True
                messages.add_message(request, messages.ERROR, "{} : {}-{} ({})=> error".format(specialty.name,
                                                                                               organization.reference,
                                                                                               organization.name,
                                                                                               period.name))

    if not check_error_present and num_periods > 0:
        mdl_int.internship_student_affectation_stat.delete_affectations(student, cohort)
        for num_period in range(0, num_periods):
            if organizations[num_period]:
                organization = mdl_int.organization.search(cohort=cohort, reference=organizations[num_period])[0]
                specialty = mdl_int.internship_speciality.search(cohort=cohort, name=specialties[num_period])[0]
                period = mdl_int.period.search(cohort=cohort, name=periods[num_period])[0]
                student_choices = mdl_int.internship_choice.search(student=student, speciality=specialty)
                internship = mdl_int.internship.get_by_id(internships[num_period])
                affectation = mdl_int.internship_student_affectation_stat.build(student, organization, specialty,
                                                                                period, internship,
                                                                                student_choices)
                affectation.save()

        redirect_url = reverse('internships_student_read', kwargs={"cohort_id": cohort.id, "student_id": student.id})
    else:
        redirect_url = reverse('internship_student_affectation_modification', kwargs={"cohort_id": cohort.id,
                                                                                      "student_id": student.id})
    return HttpResponseRedirect(redirect_url)


@login_required
@require_POST
@permission_required('internship.is_internship_manager', raise_exception=True)
def import_students(request, cohort_id):
    cohort = get_object_or_404(mdl_int.cohort.Cohort, pk=cohort_id)

    form = StudentsImportActionForm(request.POST, request.FILES)
    if form.is_valid():
        file_upload = form.cleaned_data['file_upload']
        import_xlsx(cohort, BytesIO(file_upload.read()))
    return HttpResponseRedirect(reverse('internships_student_resume', kwargs={"cohort_id": cohort_id}))


def _get_affectation_for_period(affectations, period):
    for affectation in affectations:
        if affectation.period == period:
            return affectation
    return None


def _get_students_with_status(cohort):
    students_status = []
    students_informations = mdl_int.internship_student_information.find_all(cohort)
    for student_info in students_informations:
        person = student_info.person
        student = mdl.student.find_by_person(person)
        student_status = _get_student_status(student, cohort)
        students_status.append((student, student_status))
    return students_status


def _get_student_status(student, cohort):
    internship_ids = mdl_int.internship.Internship.objects.filter(cohort=cohort, pk__gte=1).values_list("pk", flat=True)
    choices_values = mdl_int.internship_choice.get_choices_made(cohort=cohort,
                                                                student=student).values_list("internship_id", flat=True)
    return len(list(set(internship_ids) - set(choices_values))) == 0
