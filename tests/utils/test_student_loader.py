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
import factory.fuzzy


class CsvRowFactory:
    name = factory.Faker('name')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')

    gender = 'F'

    birthdate = '2011-01-21'
    birthplace = factory.Faker('city')

    nationality = 'Belge'

    noma = factory.Faker('numerify', text='##########')
    fgs = factory.Faker('numerify', text='######')

    street = factory.Faker('lexify', text='??????')
    postal_code = factory.Faker('zipcode')
    city = factory.Faker('city')
    country = factory.Faker('country')
    phone_mobile = factory.Faker('phone_number')
    email = factory.Faker('email')


def generate_record(registration_id):
    row = CsvRowFactory()
    return (
        'MD2MS/G',
        '22',
        '{}, {}'.format(row.last_name.generate({}), row.first_name.generate({})),
        # row.name.generate({}),
        row.gender,
        row.birthdate,
        row.birthplace.generate({}),
        row.nationality,
        registration_id,
        row.fgs.generate({}),
        row.street.generate({}),
        row.postal_code.generate({}),
        row.city.generate({}),
        row.country.generate({}),
        row.phone_mobile.generate({}),
        row.phone_mobile.generate({}),
        row.street.generate({}),
        row.postal_code.generate({}),
        row.city.generate({}),
        row.country.generate({}),
        row.email.generate({}),
        row.email.generate({}),
        row.street.generate({}),
        row.postal_code.generate({}),
        row.city.generate({}),
        row.country.generate({}),
    )
