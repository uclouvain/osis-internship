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
import csv

import pendulum
from django.contrib.auth.models import Group

from base.models.person import Person
from internship.models.internship_student_information import InternshipStudentInformation


def import_csv(cohort, csvfile):
    reader = csv.reader(csvfile)
    next(reader)
    for row in reader:
        name, gender, birthdate, birthplace, nationality, noma, \
            fgs, street, zipcode, city, country, phone, email = row

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
            'cohort': cohort,
        }
        student_info = InternshipStudentInformation.objects.create(**info)

        if person.user:
            group = Group.objects.get(name='internship_students')
            person.user.groups.add(group)
