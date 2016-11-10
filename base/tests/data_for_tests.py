##############################################################################
#
# OSIS stands for Open Student Information System. It's an application
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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from base import models as mdl_base
import datetime


def create_person(first_name, last_name):
    person = mdl_base.person.Person(first_name=first_name, last_name=last_name)
    person.save()
    return person


def create_student(first_name, last_name, registration_id):
    person = create_person(first_name, last_name)
    student = mdl_base.student.Student(person=person, registration_id=registration_id)
    student.save()
    return student


def create_academic_year(year=2016):
    an_academic_year = mdl_base.academic_year.AcademicYear()
    an_academic_year.year = year
    an_academic_year.save()
    return an_academic_year


def create_learning_unit(acronym, title):
    learning_unit = mdl_base.learning_unit.LearningUnit(acronym=acronym, title=title,
                                                        start_year=2010)
    learning_unit.save()
    return learning_unit


def create_learning_unit_year(acronym, title, academic_year):
    learning_unit_year = \
        mdl_base.learning_unit_year.LearningUnitYear(acronym=acronym, title=title,
                                                     academic_year=academic_year,
                                                     learning_unit=create_learning_unit(acronym, title))
    learning_unit_year.save()
    return learning_unit_year


def create_date_enrollment():
    return datetime.date.today()


def create_offer(title):
    offer = mdl_base.offer.Offer(title=title)
    offer.save()
    return offer


def create_offer_year(acronym, title, academic_year):
    offer_year = mdl_base.offer_year.OfferYear(offer=create_offer(title), academic_year=academic_year,
                                               acronym=acronym, title=title)
    offer_year.save()
    return offer_year


def create_offer_enrollment(student, offer_year):
    offer_enrollment = mdl_base.offer_enrollment.OfferEnrollment(date_enrollment=create_date_enrollment(),
                                                                 student=student, offer_year=offer_year)
    offer_enrollment.save()
    return offer_enrollment


def create_learning_unit_enrollment(learning_unit_year, offer_enrollment):
    learning_unit_enrollment = \
        mdl_base.learning_unit_enrollment.LearningUnitEnrollment(date_enrollment=create_date_enrollment(),
                                                                 learning_unit_year=learning_unit_year,
                                                                 offer_enrollment=offer_enrollment)
    learning_unit_enrollment.save()
    return learning_unit_enrollment


def create_academic_calendar(academic_year):
    academic_calendar = mdl_base.academic_calendar.AcademicCalendar(academic_year=academic_year)
    academic_calendar.save()
    return academic_calendar


def create_offer_year_calendar(offer_year, academic_year):
    offer_year_calendar = \
        mdl_base.offer_year_calendar.OfferYearCalendar(offer_year=offer_year,
                                                       academic_calendar=create_academic_calendar(academic_year))
    offer_year_calendar.save()
    return offer_year_calendar


def create_session_exam(number_session, learning_unit_year, offer_year_calendar):
    session_exam = mdl_base.session_exam.SessionExam(number_session=number_session,
                                                     learning_unit_year=learning_unit_year,
                                                     offer_year_calendar=offer_year_calendar)
    session_exam.save()
    return session_exam


def create_exam_enrollment(session_exam, learning_unit_enrollment):
    exam_enrollment = mdl_base.exam_enrollment.ExamEnrollment(session_exam=session_exam,
                                                              learning_unit_enrollment=learning_unit_enrollment)
    exam_enrollment.save()
    return exam_enrollment


