import csv

import pendulum
from django.contrib.auth.models import Group

from base.models.person import Person
from internship.models.internship_student_information import InternshipStudentInformation


def import_csv(self, csvfile):
    reader = csv.reader(csvfile)
    next(reader)
    for row in reader:
        name, gender, birthdate, birthplace, nationality, noma, fgs, street, zipcode, city, country, phone, email = row

        person = Person.objects.filter(global_id=noma).first()

        print(person)

        if not person:
            if ',' in name:
                t = name.split(',')
                first_name, last_name = t[0].strip(), t[1].strip()
            else:
                t = name.split()
                first_name, last_name = ' '.join(t[:-1]).strip(), t[-1].strip()

            d = pendulum.parse(birthdate)

            birthdate = d.format('%Y-%m-%d')

            person = Person.objects.create(
                global_id=noma,
                gender=gender,
                first_name=first_name,
                last_name=last_name,
                birth_date=birthdate
            )

        info = {
            'person': person,
            'country': country,
            'postal_code': zipcode,
            'email': email,
            'phone_mobile': phone,
            'city': city,
        }
        student_info = InternshipStudentInformation.objects.create(**info)
        # print(student_info.id)
        if person.user:
            group = Group.objects.get(name='internship_students')
            person.user.groups.add(group)
