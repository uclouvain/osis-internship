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

from collections import OrderedDict
from operator import itemgetter
from django.utils import timezone
from django.core.serializers.json import DjangoJSONEncoder

from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from internship.business import assignment, statistics
from internship import models
from internship.models import internship_student_affectation_stat
from internship.utils.exporting import score_encoding_xls
from internship.views.internship import set_tabs_name


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def run_affectation(request, cohort_id):
    cohort = get_object_or_404(models.cohort.Cohort, pk=cohort_id)
    if request.method == 'POST':
        start_date_time = timezone.now()  # To register the beginning of the algorithm.

        slvr = assignment.Assignment(cohort)
        slvr.solve()
        slvr.persist_solution()
        end_date_time = timezone.now()  # To register the end of the algorithm.

        affectation_generation_time = models.affectation_generation_time.AffectationGenerationTime()
        affectation_generation_time.cohort = cohort
        affectation_generation_time.start_date_time = start_date_time
        affectation_generation_time.end_date_time = end_date_time
        affectation_generation_time.generated_by = request.user.username
        affectation_generation_time.save()
    return redirect(reverse('internship_affectation_hospitals',  kwargs={'cohort_id': cohort.id}))


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def view_hospitals(request, cohort_id):
    cohort = get_object_or_404(models.cohort.Cohort, pk=cohort_id)
    sol, table, stats, internship_errors = None, None, None, None
    periods = models.period.Period.objects.filter(cohort=cohort).order_by('date_end')
    period_ids = periods.values_list("id", flat=True)

    student_affectations = internship_student_affectation_stat.InternshipStudentAffectationStat.objects\
        .filter(period_id__in=period_ids)\
        .select_related("student", "organization", "speciality", "period")

    if student_affectations.count() > 0:
        table = statistics.load_solution_table(student_affectations, cohort)
        # Mange sort of the organizations
        table.sort(key=itemgetter(0))

    latest_generation = models.affectation_generation_time.get_latest(cohort)

    context = {'cohort': cohort, 'periods': periods, 'organizations': table, 'latest_generation': latest_generation}

    return render(request, "internship_affectation_hospitals.html", context)


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def view_students(request, cohort_id):
    cohort = get_object_or_404(models.cohort.Cohort, pk=cohort_id)
    sol, tabl = None, None
    periods = models.period.Period.objects.filter(cohort=cohort).order_by('date_end')
    period_ids = periods.values_list("id", flat=True)

    student_affectations = internship_student_affectation_stat.InternshipStudentAffectationStat.objects\
        .filter(period_id__in=period_ids)\
        .select_related(
            "student",
            "student__person",
            "internship",
            "internship__speciality",
            "organization",
            "speciality",
            "period"
        )

    if student_affectations.count() > 0:
        sol = statistics.load_solution_sol(cohort, student_affectations)
        # Mange sort of the students
        sol = OrderedDict(sorted(sol.items(), key=lambda t: t[0].person.last_name))

    latest_generation = models.affectation_generation_time.get_latest(cohort)

    context = {'cohort': cohort, 'periods': periods, 'recap_sol': sol, 'latest_generation': latest_generation}

    return render(request, "internship_affectation_students.html", context)


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def view_statistics(request, cohort_id):
    cohort = get_object_or_404(models.cohort.Cohort, pk=cohort_id)
    sol, table, stats = None, None, None
    periods = models.period.Period.objects.filter(cohort=cohort).order_by('date_end')
    period_ids = periods.values_list("id", flat=True)

    student_affectations = internship_student_affectation_stat.InternshipStudentAffectationStat.objects\
        .filter(period_id__in=period_ids)\
        .select_related(
            "student",
            "student__person",
            "internship",
            "internship__speciality",
            "organization",
            "speciality",
            "period"
        )

    if student_affectations.count() > 0:
        sol = statistics.load_solution_sol(cohort, student_affectations)
        stats = statistics.compute_stats(cohort, sol)

    latest_generation = models.affectation_generation_time.get_latest(cohort)

    context = {'cohort': cohort, 'stats': stats, 'latest_generation': latest_generation}

    return render(request, "internship_affectation_statistics.html", context)


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def view_errors(request, cohort_id):
    cohort = get_object_or_404(models.cohort.Cohort, pk=cohort_id)
    internship_errors = None
    periods = models.period.Period.objects.filter(cohort=cohort).order_by('date_end')
    period_ids = periods.values_list("id", flat=True)

    student_affectations = internship_student_affectation_stat.InternshipStudentAffectationStat.objects\
        .filter(period_id__in=period_ids)\
        .select_related("student", "organization", "speciality", "period")

    if student_affectations.count() > 0:
        hospital = models.organization.get_hospital_error(cohort)
        internship_errors = internship_student_affectation_stat.InternshipStudentAffectationStat.objects \
            .filter(organization=hospital, period_id__in=period_ids)

    latest_generation = models.affectation_generation_time.get_latest(cohort)
    context = {'cohort': cohort, 'errors': internship_errors, 'latest_generation': latest_generation}
    return render(request, "internship_affectation_errors.html", context)


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def export_score_encoding_xls(request, cohort_id):
    cohort = get_object_or_404(models.cohort.Cohort, pk=cohort_id)
    workbook = score_encoding_xls.export_xls(cohort)
    response = HttpResponse(workbook, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    file_name = "encodage_notes_{}.xlsx".format(cohort.name.strip().replace(' ', '_'))
    response['Content-Disposition'] = 'attachment; filename={}'.format(file_name)
    return response


@login_required
@permission_required('internship.is_internship_manager', raise_exception=True)
def internship_affectation_sumup(request, cohort_id):
    cohort = get_object_or_404(models.cohort.Cohort, pk=cohort_id)
    filter_specialty, filter_hospital = int(request.GET.get('specialty', 0)), int(request.GET.get('hospital', 0))
    specialty = models.internship_speciality.get_by_id(filter_specialty)
    hospital = models.organization.get_by_id(filter_hospital)
    all_speciality = list(models.internship_speciality.find_all(cohort=cohort))
    all_speciality = models.internship_speciality.set_speciality_unique(all_speciality)
    periods = models.period.search(cohort=cohort).order_by('date_end')
    organizations = models.organization.search(cohort=cohort)
    organizations = models.organization.sort_organizations(organizations)
    offers = models.internship_offer.search(cohort=cohort)

    hospital_specialties = {
        "all" : []
    }
    for specialty in all_speciality :
        hospital_specialties["all"].append({
                    "id": specialty.id,
                    "name": specialty.name
        })

    informations = []
    for organization in organizations:
        hospital_specialties[organization.reference] = []
        for offer in offers:
            if offer.organization.reference == organization.reference:
                if offer.speciality_id == filter_specialty:
                    informations.append(offer)
                hospital_specialties[organization.reference].append({
                    "id": offer.speciality.id,
                    "name": offer.speciality.name
                })
    hospital_specialties = json.dumps(hospital_specialties, cls=DjangoJSONEncoder)

    affectations = {}
    if filter_specialty != 0:
        all_affectations = list(models.internship_student_affectation_stat.search(speciality_id=filter_specialty))
        temp_affectations = {}
        for period in periods:
            temp_temp_affectations = []
            for aff in all_affectations:
                if aff.period == period:
                    temp_temp_affectations.append(aff)
            temp_affectations[period.name] = temp_temp_affectations
        affectations = temp_affectations

    context = {'cohort': cohort, 'active_hospital': hospital, 'active_specialty': specialty,
               'hospitals': organizations, 'hospital_specialties': hospital_specialties,
               'specialties': all_speciality, 'affectations': affectations,
               'periods': periods, 'informations': informations,}
    
    return render(request, "internship_affectation_sumup.html", context)
