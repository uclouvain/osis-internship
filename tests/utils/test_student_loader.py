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
from factory.faker import faker
generator = faker.Faker()



class CsvRowFactory:
    name = faker.Faker().name()
    first_name = faker.Faker().first_name()
    last_name = faker.Faker().last_name()

    gender = 'F'

    birthdate = '2011-01-21'
    birthplace = faker.Faker().city()

    nationality = 'Belge'

    noma = faker.Faker().numerify(text='##########')
    fgs = faker.Faker().numerify(text='######')

    street = faker.Faker().lexify(text='??????')
    postal_code = faker.Faker().zipcode()
    city = faker.Faker().city()
    country = faker.Faker().country()
    phone_mobile = faker.Faker().phone_number()
    email = faker.Faker().email()


def generate_record(registration_id):
    row = CsvRowFactory()
    return (
        'MD2MS/G',
        '22',
        f'{row.last_name}, {row.first_name}',
        row.gender,
        row.birthdate,
        row.birthplace,
        row.nationality,
        registration_id,
        row.fgs,
        row.street,
        row.postal_code,
        row.city,
        row.country,
        row.phone_mobile,
        row.phone_mobile,
        row.street,
        row.postal_code,
        row.city,
        row.country,
        row.email,
        row.email,
        row.street,
        row.postal_code,
        row.city,
        row.country,
    )
