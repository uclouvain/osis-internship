from django.template.defaulttags import register

from internship.models.master_allocation import MasterAllocation


@register.simple_tag
def get_master_name(specialty, organization, cohort):
    main_master_allocation = MasterAllocation.objects.filter(
        specialty__name=specialty['name'],
        organization__name=organization['name'],
        specialty__cohort__name=cohort,
    ).first()
    return main_master_allocation.master.person if main_master_allocation else None


@register.filter
def display_short_person_name(person):
    if not person:
        return '-'
    return f"{person.last_name.upper()}, {person.first_name and person.first_name.upper()[0]}"
