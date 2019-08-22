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
import json
from io import BytesIO

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Prefetch, OuterRef, Subquery, Value
from django.db.models.functions import Concat
from django.forms import model_to_dict
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_POST

from base import models as mdl
from base.models.person_address import PersonAddress
from base.models.student import Student
from internship import models as mdl_int
from internship.forms.form_student_information import StudentInformationForm
from internship.forms.students_import_form import StudentsImportActionForm
from internship.models.cohort import Cohort
from internship.models.internship import Internship
from internship.models.internship_choice import InternshipChoice
from internship.models.internship_speciality import InternshipSpeciality
from internship.models.internship_student_affectation_stat import InternshipStudentAffectationStat
from internship.models.internship_student_information import InternshipStudentInformation
from internship.models.master_allocation import MasterAllocation
from internship.models.organization import Organization
from internship.models.period import Period
from internship.utils.importing.import_students import import_xlsx
from internship.views.common import display_errors, get_object_list
from reference.models import country


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def internships_student_resume(request, cohort_id):
    cohort = get_object_or_404(mdl_int.cohort.Cohort, pk=cohort_id)
    internships_ids = cohort.internship_set.values_list('id',flat=True)
    filter_name = request.GET.get('name', '')
    page = request.GET.get('page')
    choices = InternshipChoice.objects.filter(internship_id__in=internships_ids).select_related('student')
    number_students_ok, number_students_not_ok = _get_statuses(choices, internships_ids)
    students_with_status = _get_students_with_status(request, page, cohort, filter_name)
    student_with_internships = mdl_int.internship_choice.get_number_students(cohort)
    students_can_have_internships = mdl_int.internship_student_information.get_number_students(cohort)
    student_without_internship = students_can_have_internships - student_with_internships
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
def student_form(request, cohort_id, form=None):
    cohort = get_object_or_404(mdl_int.cohort.Cohort, pk=cohort_id)
    countries = country.find_all()
    if form is None:
        form = StudentInformationForm(request.POST)
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
            data = {'error': str(_('Student already exists'))}
    else:
        data = {'error': str(_('Student does not exist'))}

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
        display_errors(request, errors)
        return HttpResponseRedirect(reverse("internship_student_form", args=[cohort_id]))

    return HttpResponseRedirect(reverse("internships_student_resume", args=[cohort_id]))


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def internships_student_read(request, cohort_id, student_id):
    cohort = get_object_or_404(Cohort, pk=cohort_id)
    student = Student.objects.get(id=student_id)
    student.address = PersonAddress.objects.get(person=student.person)

    if not request.user.has_perm('internship.is_internship_manager'):
        person_who_read = mdl.person.find_by_user(request.user)
        student_who_read = mdl.student.find_by_person(person_who_read)
        if not student_who_read or not student or student_who_read.pk != student.pk:
            raise PermissionDenied(request)

    if not student:
        return render(request, "student.html", {'errors': ['student_doesnot_exist']})

    information = InternshipStudentInformation.objects.get(person=student.person, cohort=cohort)
    internships = Internship.objects.filter(cohort=cohort).select_related('speciality').order_by('speciality', 'name')
    internship_choices = InternshipChoice.objects.filter(
        internship__in=internships, student=student
    ).order_by('choice').select_related('organization', 'speciality')
    specialities = InternshipSpeciality.objects.filter(mandatory=True, cohort=cohort).order_by('acronym', 'name')
    master = MasterAllocation.objects.filter(specialty=OuterRef('speciality'), organization=OuterRef('organization'))
    affectations = InternshipStudentAffectationStat.objects.filter(
        student=student, period__cohort=cohort
    ).select_related(
        'speciality', 'organization', 'period', 'period__cohort', 'internship', 'internship__speciality'
    ).order_by(
        "period__date_start"
    ).annotate(
        master=Concat(
            Subquery(master.values('master__last_name')[:1]),
            Value(', '),
            Subquery(master.values('master__first_name')[:1])
        )
    )
    periods = Period.objects.filter(cohort=cohort).order_by("date_start")
    organizations = Organization.objects.filter(cohort=cohort)
    return render(request, "student.html", locals())


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def internship_student_information_modification(request, cohort_id, student_id, form=None):
    cohort = get_object_or_404(mdl_int.cohort.Cohort, pk=cohort_id)
    student = mdl.student.find_by_id(student_id)
    information = mdl_int.internship_student_information.search(person=student.person, cohort=cohort).first()
    if form is None:
        form = StudentInformationForm(instance=information)
    return render(request, "student_information_modification.html", locals())


@login_required
@require_POST
@permission_required('internship.is_internship_manager', raise_exception=True)
def student_save_information_modification(request, cohort_id, student_id):
    cohort = get_object_or_404(mdl_int.cohort.Cohort, pk=cohort_id)
    student = mdl.student.find_by_id(student_id)
    information = mdl_int.internship_student_information.find_by_person(student.person, cohort)
    if not information:
        information = mdl_int.internship_student_information.InternshipStudentInformation()
        information.person = student.person
    else:
        information = information.first()

    if information.cohort is None:
        information.cohort = cohort

    data = request.POST.copy()
    data.update({'person': student.person.id, 'cohort': cohort_id})
    form = StudentInformationForm(data, instance=information)

    if form.is_valid():
        information.email = form.cleaned_data.get('email')
        information.phone_mobile = form.cleaned_data.get('phone_mobile')
        information.location = form.cleaned_data.get('location')
        information.postal_code = form.cleaned_data.get('postal_code')
        information.city = form.cleaned_data.get('city')
        information.country = str(form.cleaned_data.get('country'))
        information.contest = form.cleaned_data.get('contest')
        information.save()
    else:
        return internship_student_information_modification(request, cohort_id, student_id, form)

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

    modalities = mdl_int.internship.find_by_cohort(cohort).order_by("name")

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
                internship = None
                if internships[num_period]:
                    internship = mdl_int.internship.get_by_id(internships[num_period])
                affectation = mdl_int.internship_student_affectation_stat.build(student, organization, specialty,
                                                                                period, internship, student_choices)
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
    errors = []
    if form.is_valid():
        file_upload = form.cleaned_data['file_upload']
        differences = import_xlsx(cohort, BytesIO(file_upload.read()))
        if differences:
            return internships_student_import_update(request, cohort_id, differences)
    else:
        errors.append(form.errors)
        display_errors(request, errors)

    return HttpResponseRedirect(reverse('internships_student_resume', kwargs={"cohort_id": cohort_id}))


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def internships_student_import_update(request, cohort_id, differences=None):
    """Render a view to visualize and accept differences to be applied"""
    cohort = get_object_or_404(mdl_int.cohort.Cohort, pk=cohort_id)
    if request.POST.get('data'):
        data = json.loads(request.POST.get('data'))
        for student_information in data:
            if student_information['id']:
                existing_student = InternshipStudentInformation.objects.get(pk=student_information['id'], cohort=cohort)
            else:
                existing_student = InternshipStudentInformation(
                    person_id=student_information['person'],
                    cohort_id=cohort_id
                )
                student_information['id'] = existing_student.id
            for field in student_information:
                existing_student.__dict__[field] = student_information[field]
            existing_student.save()
        return HttpResponseRedirect(reverse('internships_student_resume', kwargs={"cohort_id": cohort_id}))
    data_json, new_records_count = _convert_differences_to_json(differences)
    return render(request, "students_update.html", locals())


def _get_affectation_for_period(affectations, period):
    for affectation in affectations:
        if affectation.period == period:
            return affectation
    return None


def _get_students_with_status(request, page, cohort, filter_name):

    students_status = []

    students_info = InternshipStudentInformation.objects\
        .filter(cohort=cohort)\
        .select_related('person') \
        .prefetch_related(Prefetch('person__student_set', to_attr='students'))\
        .order_by('person__last_name', 'person__first_name')

    if filter_name:
        students_info = students_info.filter(person__last_name__icontains=filter_name) | \
                                  students_info.filter(person__first_name__icontains=filter_name)

    paginated_students_info = get_object_list(request, students_info)

    internship_ids = mdl_int.internship.Internship.objects.filter(cohort=cohort, pk__gte=1).values_list("pk", flat=True)

    for student_info in paginated_students_info.object_list:
        student_status = _get_student_status(student_info.person.students[0], cohort, internship_ids)
        students_status.append((student_info.person.students[0], student_status))
    paginated_students_info.object_list = students_status
    return paginated_students_info


def _get_student_status(student, cohort, internship_ids):
    choices_values = mdl_int.internship_choice.get_choices_made(cohort=cohort,
                                                                student=student).values_list("internship_id", flat=True)
    return len(list(set(internship_ids) - set(choices_values))) == 0


def _convert_differences_to_json(differences):
    data_json = []
    new_records_count = 0
    for diff in differences:
        data_json.append(model_to_dict(diff['data']))
        if diff['new_record']:
            new_records_count += 1
    data_json = json.dumps(data_json, cls=DjangoJSONEncoder)
    return data_json, new_records_count


def _get_statuses(choices, internships_ids):
    statuses = {}
    number_ok = 0
    number_not_ok = 0
    for choice in choices:
        person_id = choice.student.person_id
        if person_id in statuses.keys() and choice.internship_id not in statuses[person_id]:
            statuses[person_id].append(choice.internship_id)
        if person_id not in statuses.keys():
            statuses[person_id] = []
    for person_id in statuses.keys():
        if len(internships_ids) == len(statuses[person_id]):
            number_ok += 1
        else:
            number_not_ok += 1
    return number_ok, number_not_ok
