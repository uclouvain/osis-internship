import uuid

from internship.models import internship
from internship.models import internship_speciality
from internship.models import master_allocation
from internship.models import organization
from internship.models.internship_place_evaluation_item import PlaceEvaluationItem
from internship.models.internship_speciality import InternshipSpeciality
from internship.models.period import Period


def copy_from_origin(cohort):
    if cohort.originated_from:
        _copy_organizations(cohort.originated_from, cohort)
        _copy_specialties(cohort.originated_from, cohort)
        _copy_periods(cohort.originated_from, cohort)
        _copy_internships(cohort.originated_from, cohort)
        copy_master_allocations(cohort.originated_from, cohort)
        _copy_place_evaluation_items(cohort.originated_from, cohort)


def _copy_organizations(cohort_from, cohort_to):
    organizations = organization.find_by_cohort(cohort_from)
    for org in organizations:
        org.pk = None
        org.uuid = uuid.uuid4()
        org.cohort = cohort_to
        org.save()


def _copy_specialties(cohort_from, cohort_to):
    specialities = internship_speciality.find_by_cohort(cohort_from)
    for speciality in specialities:
        speciality.pk = None
        speciality.uuid = uuid.uuid4()
        speciality.cohort = cohort_to
        speciality.save()


def _copy_periods(cohort_from, cohort_to):
    periods = Period.objects.filter(cohort=cohort_from).order_by("date_start")
    for prd in periods:
        prd.pk = None
        prd.uuid = uuid.uuid4()
        prd.cohort = cohort_to
        prd.save()


def _copy_internships(cohort_from, cohort_to):
    """ This function must come after _copy_specialties because it needs the new ones. """
    internships = internship.find_by_cohort(cohort_from)
    for intern in internships:
        intern.pk = None
        intern.cohort = cohort_to
        intern.uuid = uuid.uuid4()
        intern.speciality = _get_new_cohort_specialty(intern.speciality, cohort_to)
        intern.save()


def copy_master_allocations(cohort_from, cohort_to, selected_allocations=None):
    """ This function must come after _copy_organizations and _copy_specialties because it needs the new ones. """

    allocations = selected_allocations if selected_allocations else master_allocation.find_by_cohort(cohort_from)

    for allocation in allocations:
        allocation.pk = None
        allocation.uuid = uuid.uuid4()
        allocation.organization = _get_new_cohort_hospital(allocation.organization, cohort_to)
        allocation.specialty = _get_new_cohort_specialty(allocation.specialty, cohort_to)
        allocation.save()


def _get_new_cohort_specialty(previous_specialty, cohort_to):
    if previous_specialty:
        specialties = InternshipSpeciality.objects.filter(cohort=cohort_to).filter(acronym=previous_specialty.acronym)
        if specialties:
            return specialties.first()
    return None


def _get_new_cohort_hospital(previous_hospital, cohort_to):
    if previous_hospital:
        organizations = organization.find_by_reference(cohort_to, previous_hospital.reference)
        if organizations:
            return organizations.first()
    return None


def _copy_place_evaluation_items(cohort_from, cohort_to):
    items = PlaceEvaluationItem.objects.filter(cohort=cohort_from)
    for item in items:
        item.pk = None
        item.cohort = cohort_to
        item.uuid = uuid.uuid4()
        item.save()
