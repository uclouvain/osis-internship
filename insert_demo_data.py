#!/usr/bin/env python3

from functools import reduce
import os

# Add your fixtures at the end of the list so that model dependencies are respected.
DATA_FIXTURES = [
    'user.json',
    'person.json',
    'tutor.json',
    'student.json',
    'academic_year.json',
    'academic_calendar.json',
    'learning_unit.json',
    'learning_unit_year.json',
    'messages_templates.json',
    'offer.json',
    'organization.json',
    'structure.json',
    'attribution.json',
    'continent.json',
    'currency.json',
    'country.json',
    'decree.json',
    'domain.json',
    'education_institution.json',
    'language.json',
    'continent.json',
    'person_address.json',
    'organization_address.json',
    'offer_year.json',
    'offer_year_calendar.json',
    'session_exam.json',
    'program_manager.json',
    'offer_enrollment.json',
    'learning_unit_enrollment.json',
    'exam_enrollment.json'
    ]

ARGS = reduce(lambda s1,s2 : s1 + ' ' + s2,DATA_FIXTURES)
COMMAND = 'python manage.py loaddata '+ARGS
print(COMMAND)
os.system(COMMAND)
