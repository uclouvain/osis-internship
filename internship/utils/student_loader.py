import collections
import csv

import django.db
from django.contrib.auth.models import Group

from base.models import person as mdl_person
from internship.models import internship_student_information as mdl_isi

CSVRow = collections.namedtuple(
    'CSVRow',
    ['name', 'gender', 'birthdate', 'birthplace', 'nationality', 'noma',
     'fgs', 'street', 'postal_code', 'city', 'country', 'phone_mobile', 'email']
)

Status = collections.namedtuple(
    'Status',
    ['idx', 'imported', 'not_found', 'duplicated', 'error']
)


class BadCSVFormat(Exception):
    pass


def load_internship_students(fp_like, has_header=True):
    try:
        dialect = csv.Sniffer().sniff(fp_like.readline(), [',', ';'])
    except csv.Error:
        raise BadCSVFormat()

    fp_like.seek(0)
    reader = csv.reader(fp_like, dialect)

    if has_header:
        next(reader, None)

    generator = (CSVRow(*item) for item in reader)

    statuses = []
    for idx, row in enumerate(generator):
        status = _insert_internship_student_information(idx, row)
        statuses.append(status)
    return statuses


def _insert_internship_student_information(idx, row):
    values = dict.fromkeys(['not_found', 'imported', 'duplicated', 'error'], False)
    values['idx'] = idx

    person = mdl_person.find_by_global_id(row.noma)
    if not person:
        values['not_found'] = True
    else:
        student = mdl_isi.InternshipStudentInformation()
        student.person = person
        student.location = row.street
        student.postal_code = row.postal_code
        student.city = row.city
        student.country = row.country
        student.phone_mobile = row.phone_mobile
        student.email = row.email

        try:
            student.save()
            if person.user:
                group = Group.objects.get(name='internship_students')
                person.user.groups.add(group)
            values['imported'] = True
        except django.db.IntegrityError:
            values['duplicated'] = True
        except (django.db.DataError, Exception) as ex:
            values['error'] = True

    status = Status(**values)
    return status
