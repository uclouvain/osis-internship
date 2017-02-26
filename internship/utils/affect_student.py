##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2016 Université catholique de Louvain (http://www.uclouvain.be)
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


def assign_internships(offers, choices, priority_choices):
    pass


def input_file(filename):
    with open(filename) as file:
        number_offers, number_choices = convert_line_to_ints(file.readline())
        file.readline()
        offers = extract_offers(file, number_offers)
        file.readline()
        choices, priority_choices = extract_choices(file, number_choices)
        return offers, choices, priority_choices


def extract_offers(file, number_offers):
    offers = dict()
    for x in range(0, number_offers):
        offer = convert_line_to_ints(file.readline())
        offers[(offer[1], offer[2])] = offer
    return offers


def extract_choices(file, number_choices):
    choices = dict()
    priority_choices = dict()
    for x in range(0, number_choices):
        choice = convert_line_to_ints(file.readline())
        key = (choice[0], choice[3], choice[2])
        if is_a_priority(choice):
            add_choice(choice, priority_choices, key)
        else:
            add_choice(choice, choices, key)
    return choices, priority_choices


def add_choice(choice, choices, key):
    if key in choices:
        choices[key].append(choice)
    else:
        choices[key] = [choice]


def is_a_priority(choice):
    return bool(choice[5])


def convert_line_to_ints(line):
    return [int(x) for x in line.split()]
