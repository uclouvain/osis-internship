import uuid
from internship.models import organization
from internship.models import internship_speciality
from internship.models import period
from internship.models import master_allocation


def copy_from_origin(cohort):
    if cohort.originated_from:
        _copy_organizations(cohort.originated_from, cohort)
        _copy_specialties(cohort.originated_from, cohort)
        _copy_periods(cohort.originated_from, cohort)
        _copy_master_allocations(cohort.originated_from, cohort)


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
    periods = period.find_by_cohort(cohort_from)
    for prd in periods:
        prd.pk = None
        prd.uuid = uuid.uuid4()
        prd.cohort = cohort_to
        prd.save()


def _copy_master_allocations(cohort_from, cohort_to):
    """ This function must come after _copy_organizations and _copy_specialties because it needs the new ones. """
    allocations = master_allocation.find_by_cohort(cohort_from)

    for allocation in allocations:
        allocation.pk = None

        if allocation.organization:
            organizations = organization.find_by_reference(cohort_to, allocation.organization.reference)
            if organizations:
                allocation.organization = organizations.first()

        if allocation.specialty:
            specialties = internship_speciality.find_by_acronym(cohort_to, allocation.specialty.acronym)
            if specialties:
                allocation.specialty = specialties.first()

        allocation.save()
