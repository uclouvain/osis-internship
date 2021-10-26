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
import itertools
import json
from io import BytesIO

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.db.models import Prefetch, OuterRef, Subquery, Value, Q, Count, F
from django.db.models.functions import Concat
from django.forms import model_to_dict
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils.datetime_safe import date
from django.utils.translation import gettext_lazy as _
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
from reference.models.country import Country


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def internships_student_resume(request, cohort_id):
    cohort = get_object_or_404(mdl_int.cohort.Cohort, pk=cohort_id)
    filter_name = request.GET.get('name', '')
    filter_current_internship = request.GET.get('current_internship')
    students, status_stats = _get_students_with_status(request, cohort, (filter_name, filter_current_internship))
    students_can_have_internships = mdl_int.internship_student_information.get_number_students(cohort)
    number_generalists = mdl_int.internship_student_information.get_number_of_generalists(cohort)
    number_specialists = students_can_have_internships - number_generalists
    context = {
        'search_name': None,
        'search_firstname': None,
        'students': students,
        'status_stats': status_stats,
        "number_generalists": number_generalists,
        "number_specialists": number_specialists,
        'cohort': cohort,
    }
    return render(request, "students.html", context)


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def student_form(request, cohort_id, form=None):
    cohort = get_object_or_404(mdl_int.cohort.Cohort, pk=cohort_id)
    countries = Country.objects.order_by('name')
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
            Subquery(master.values('master__person__last_name')[:1]),
            Value(', '),
            Subquery(master.values('master__person__first_name')[:1])
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
    student = get_object_or_404(Student, pk=student_id)
    organizations = mdl_int.organization.search(cohort=cohort).order_by('reference')
    specialties = mdl_int.internship_speciality.find_all(cohort=cohort)
    _append_numbers_to_acronyms(specialties)
    periods = mdl_int.period.search(cohort=cohort)
    modalities = mdl_int.internship.find_by_cohort(cohort).order_by("name")
    affectations = mdl_int.internship_student_affectation_stat.search(student__pk=student_id, period__in=periods)

    internships = {
        p: next(_.internship_id for _ in a) for p, a in itertools.groupby(affectations, lambda a: a.period_id)
    }

    return render(request, "student_affectation_modification.html", locals())


def _append_numbers_to_acronyms(specialties):
    for specialty in specialties:
        number = [int(s) for s in specialty.name.split() if s.isdigit()]
        if number:
            specialty.acronym += str(number[0])


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

    student_affectations = InternshipStudentAffectationStat.objects.filter(student=student, period__cohort=cohort)
    if _has_validated_score(student_affectations):
        check_error_present = True
        messages.add_message(
            request, messages.ERROR, _(
                "Cannot edit affectations because at least one affectation has a linked validated score"
            )
        )

    if not check_error_present:
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


def _get_students_with_status(request, cohort, filters):

    active_period = Period.objects.filter(
        cohort=cohort, date_start__lte=date.today(), date_end__gte=date.today()
    ).first()

    internship_ids = Internship.objects.filter(cohort=cohort).values_list('pk', flat=True)

    current_internship_subquery = InternshipStudentAffectationStat.objects.filter(
        student__person=OuterRef('person'),
        period=active_period
    )

    student_internships_count = InternshipChoice.objects.filter(
        internship__pk__in=internship_ids,
        choice=1,
        student__person=OuterRef('person')
    ).values('student').annotate(count=Count('internship')).values('count')

    students_info = InternshipStudentInformation.objects\
        .filter(cohort=cohort)\
        .prefetch_related(Prefetch('person__student_set', to_attr='students'))\
        .order_by('person__last_name', 'person__first_name')\
        .annotate(
            current_internship=Concat(
                Subquery(current_internship_subquery.values('speciality__acronym')),
                Subquery(current_internship_subquery.values('organization__reference'))
            ),
            chosen_internships_count=Subquery(student_internships_count, output_field=models.IntegerField()),
            total_count=Value(internship_ids.count(), output_field=models.IntegerField())
        ).annotate(
            status=F('chosen_internships_count')-F('total_count')
        )

    status_stats = {
        'OK': students_info.filter(status__gte=0).count(),
        'NOK': students_info.filter(status__lt=0).count(),
        'UNKNOWN': students_info.filter(status__isnull=True).count(),
    }

    if filters:
        filter_name, filter_current_internship = filters
        if filter_name:
            students_info = students_info.filter(person__last_name__unaccent__icontains=filter_name) | \
                            students_info.filter(person__first_name__unaccent__icontains=filter_name)
        if filter_current_internship:
            students_info = students_info.exclude(Q(current_internship__isnull=True) | Q(current_internship__exact=''))

    paginated_students_info = get_object_list(request, students_info)
    return paginated_students_info, status_stats


def _convert_differences_to_json(differences):
    data_json = []
    new_records_count = 0
    for diff in differences:
        data_json.append(model_to_dict(diff['data']))
        if diff['new_record']:
            new_records_count += 1
    data_json = json.dumps(data_json, cls=DjangoJSONEncoder)
    return data_json, new_records_count


def _has_validated_score(affectations):
    return any(validated_score for validated_score in affectations.values_list('score__validated', flat=True))
