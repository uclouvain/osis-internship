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
import random

from internship import models as mdl_internship
from internship.utils.student_assignment.internship_offer_wrapper import InternshipOfferWrapper
from internship.utils.student_assignment.student_wrapper import StudentWrapper

AUTHORIZED_PERIODS = ["P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9", "P10", "P11"] # Périodes sur lesquelles on applique l'algo
NUMBER_INTERNSHIPS = len(AUTHORIZED_PERIODS) # Nbre de stages à assigner
MAX_NUMBER_INTERNSHIPS = 4 # Nbre de choix non obligatoires
REFERENCE_PERSONAL_ORGANIZATION = 601 # Stage personnel

UNAUTHORIZED_SPECIALITIES = ["SP", "SE", "MO"]


def assign_students_to_periods(self, cohort):
    sorted_internships = mdl_internship.internship.Internship.objects.filter(cohort=cohort).order_by("sorting_order")
    students = mdl_internship.student_information.StudentInformation.objects.filter(cohort=cohort)
    priority_students, regular_students = sort_students(students)
    enrollments = []

    for internship in sorted_internships:
       enrollments += assign_students_to_periods_for_internship(priority_students, internship)
       enrollments += assign_students_to_periods_for_internship(students, internship)

    enrollments.save_all()

def assign_students_to_periods_for_internship(self, students, internship):
    offers_for_internship_with_period_places = internship.offers.include("internship_period_places") # Pseudo-code
    students = students.shuffle() # Pseudo-code
    enrollments = []
    for student in students:
        enrollments += assign_choice_to_any_available_period_for_student(student, offers_for_internship_with_period_places, internship)
    return enrollments

def assign_choice_to_any_available_period_for_student(self, student, offers_for_internship_with_period_places, internship):
    student_choices_for_internship = mdl_internship.internship_choices.InternshipChoice.objects.filter(internship=internship, student=student)
    period, offer = find_available_period_for_student_choices_and_offer(student, student_choices_for_internship, offers_for_internship_with_period_places, internship.length_in_periods)
    return InternshipEnrollment.build(student=student, period=period, internship_offer=offer, internship=internship, place=offer.organization)

def find_available_period_for_choices_and_offer(self, student, choices, offers_with_places, length):
    choices = choices.order_by("choice")

    for choice in choices:
        available_period, offer = find_available_period_and_offer_for_choice(student, choice, offers_with_places, length)
        if available_period != None:
            return available_period, offer
        else:
            return first_available_period_for_any_offer(student, offers_with_places, length)

def find_available_period_and_offer_for_choice(self, student, choice, offers_with_places, length):
    periods_with_available_places = find_periods_with_places_for_offer(choice.offer, offers_with_places)
    if len(periods_with_available_places) > 0:
        return random.choice(periods_with_available_places), choice.offer
    else:
        return None, choice.offer

def find_periods_with_places_for_offer(self, offer, offers_with_places, length):
    return offers_with_places[offer.id].periods_places.select(pp.places > 0) # Pseudo-code not dealing with 2 periods internships yet

# X 1. Enlever généraliste / spécialiste
# 2. Utiliser le modèle internship
# 3. D'abord commencer par les stages ou offre > demande
# 4. Gérer nombre de périodes dans internshi
# 5. D'abord assigner les internships avec periodes > 1


def affect_student(times=1, cohort=None):
    current_student_affectations = list(_load_current_students_affectations(cohort))
    solver = init_solver(current_student_affectations, cohort)
    best_assignments, best_cost = launch_solver(solver)

    # Tourne plusieurs fois et garde celui avec le coût le plus bas
    for x in range(1, times):
        solver.reinitialize()
        solver.update_places(current_student_affectations)
        assignments, cost = launch_solver(solver)
        if cost < best_cost:
            best_assignments = assignments
            best_cost = cost

    # Sauve les assignations générées
    save_assignments_to_db(best_assignments)


def init_solver(current_students_affectations, cohort, default_organization_reference=999):
    internships          = mdl_internship.internship.Internship.objects.filter(cohort=cohort)
    default_organization = mdl_internship.organization.Organization.objects.get(
            reference = default_organization_reference,
            cohort    = cohort
        )
    periods = mdl_internship.period.Period.objects.filter(cohort=cohort, name__in=AUTHORIZED_PERIODS)

    solver = Solver(
      offers               = _load_internship_offers_and_places(cohort, periods),
      periods              = periods,
      students             = _load_students_and_choices(cohort),
      internships          = internships,
      default_organization = default_organization
    )

    solver.update_places(current_students_affectations)

    return solver


def launch_solver(solver):
    solver.solve()
    #return solver.get_solution()
    return None


def save_assignments_to_db(assignments):
    for affectation in assignments:
        affectation.save()


class Solver:
    """
        Solver to assign internships to students.
        It works by assigning first the priority students, then the oter students
        For priority students, it try first to assign one of the four choices submitted for the internship 1 by order of
        preference. Then it does the same for all the others internships (2, 3, 4, 5 and 6). If we have exhausted all
        the choices of the students, we assign the "hôpital erreur" to the student for each internship not assigned.
        For the other students, it works differently, we first try to assign all the four choices,
        if all choices cannot be assigned, we try to assign an internship of the same speciality of the choices. Also,
        when all choices are exhausted, we try to assign all possible offers to fill the internships not assigned.
        Then we assign "hôpital erreur".
    """
    def __init__(self, offers=dict(), periods=[], internships=[], students=dict(), default_organization=None):
        self.students_by_registration_id = students
        self.students = []
        self.priority_students = []
        self.priority_students_left_to_assign = []
        self.students_left_to_assign = []
        self.__classify_students(students)

        self.internships = internships

        self.offers_by_organization_speciality = offers
        self.offers_by_speciality = dict() # Sort par offre/demande
        self.__init_offers_by_speciality(offers)

        self.periods = periods
        self.default_organization = default_organization

        self.personal_offer = None

    def __classify_students(self, student_wrappers):
        # Plus besoin de faire la diff entre géné et spéci
        for student_wrapper in student_wrappers.values():
            if student_wrapper.has_priority():
                self.priority_students.append(student_wrapper)
                self.priority_students_left_to_assign.append(student_wrapper)
            else:
                self.students.append(student_wrapper)
                self.students_left_to_assign.append(student_wrapper)


    def __init_offers_by_speciality(self, offers):
        for offer in offers.values():
            if offer.internship_offer.organization.reference == str(REFERENCE_PERSONAL_ORGANIZATION):
                self.personal_offer = offer
            speciality = offer.internship_offer.speciality
            current_offers_for_speciality = self.offers_by_speciality.get(speciality.id, [])
            current_offers_for_speciality.append(offer)
            self.offers_by_speciality[speciality.id] = current_offers_for_speciality

    def update_places(self, student_affectations):
        # Jamais utilisé a priori
        for affectation in student_affectations:
            offer = self.get_offer(affectation.organization.id, affectation.speciality.id)
            student_wrapper = self.get_student(affectation.student.registration_id)
            if not offer or not student_wrapper:
                continue
            offer.occupy(affectation.period.name)
            student_wrapper.assign_specific(affectation)

    def get_student(self, registration_id):
        return self.students_by_registration_id.get(registration_id, None)

    def get_offer(self, organization_id, speciality_id):
        return self.offers_by_organization_speciality.get((organization_id, speciality_id), None)

    def get_solution(self):
        assignments = []
        cost = 0
        for student_wrapper in self.students_by_registration_id.values():
            for affectation in student_wrapper.get_assignments():
                assignments.append(affectation)
                cost += affectation.cost
        return assignments, cost

    def solve(self):
        mandatory_internships     = self.internships.filter(speciality__isnull=False)
        non_mandatory_internships = self.internships.filter(speciality__isnull=True)

        self.__assign_choices(self.priority_students_left_to_assign, mandatory_internships)
        self.__assign_choices(self.priority_students_left_to_assign, non_mandatory_internships)
        self.__assign_choices(self.students_left_to_assign, mandatory_internships)
        self.__assign_choices(self.students_left_to_assign, non_mandatory_internships)

    def __assign__choices(self, students_list, internships):
        for internship in internships:
            students_to_assign = []
            random.shuffle(students_list)
            for student in students_list:
                if student.has_all_internships_assigned(internships):
                    continue
                self.__assign_first_possible_offer_for_internship(student, internship, internships)
                students_to_assign.append(student)
            students_list = students_to_assign
        return students_list

    def __assign_first_possible_offer_for_internship(self, student_wrapper, internship, internships):
        next_internships_to_assign = student_wrapper.next_internships_to_assign(internships)
        for internship in next_internships_to_assign:
            if self.__assign_choices_or_speciality_of_choices(student_wrapper, internship):
                return
        if not student_wrapper.has_priority() and self.__assign_first_possible_offer_to_student(student_wrapper, internship):
            return
        self.__fill_student_assignment(student_wrapper)

    def __assign_choices_or_speciality_of_choices(self, student_wrapper, internship):
        if self.__assign_student_choices_for_internship(student_wrapper, internship):
            return True
        speciality = student_wrapper.get_speciality_of_internship(internship)
        if not speciality or student_wrapper.has_priority():
            return False
        if self.__assign_first_possible_offer_from_speciality_to_student(student_wrapper, speciality, internship):
            return True

###############################################


    def __assign_student_choices_for_internship_offer(self, student_wrapper, internship_offer):
        internship_choices = student_wrapper.get_choices_for_internship_offer(internship_offer)
        for choice in internship_choices:
            preference = choice.choice
            internship_offer_wrapper = self.get_offer(choice.organization.id, choice.speciality.id)
            if not internship_offer_wrapper:
                continue
            if _assign_offer_to_student(internship_offer_wrapper, internship_offer, preference, student_wrapper):
                return True
        return False

    def __assign_first_possible_offer_from_speciality_to_student(self, student_wrapper, speciality, internship_offer=0):
        offers = self.offers_by_speciality.get(speciality, [])
        offers_not_full = filter(lambda possible_offer: possible_offer.is_not_full(), offers)
        offers_permitted = filter(lambda o: is_permitted_offer(student_wrapper, o), offers_not_full)
        for offer in offers_permitted:
            _assign_offer_to_student(offer, internship_offer, 0, student_wrapper)
        return False

    def __assign_first_possible_offer_to_student(self, student_wrapper):
        if self.__assign_speciality(student_wrapper):
            return True
        elif self.__assign_personal_offer(student_wrapper, 0):
            return True
        elif self.__assign_personal_offer(student_wrapper, 1):
            return True
        return False

    def __assign_speciality(self, student_wrapper):
        # Tous ses choix, si rien n'est possible, on lui envoie une offre, n'importe laquelle du moment qu'il a accès a la spécialité
        specialities = self.offers_by_speciality.keys()
        for speciality in specialities:
            if self.__assign_first_possible_offer_from_speciality_to_student(student_wrapper, speciality):
                return True
        return False

    def __assign_personal_offer(self, student_wrapper, limit_personal_offer):
        # Choix perso, mais plus d'application ?
        if get_number_personal_offers(student_wrapper) <= limit_personal_offer:
            _assign_offer_to_student(self.personal_offer, 0, 0, student_wrapper)
            return True
        return False

    def __fill_student_assignment(self, student_wrapper):
        student_wrapper.fill_assignments(self.periods, self.default_organization)

    def reinitialize(self):
        # Réinitialise les datas
        self.students_left_to_assign = self.students[:]
        self.priority_students_left_to_assign = self.priority_students[:]
        for student_wrapper in self.students:
            student_wrapper.reinitialize()
        for student_wrapper in self.priority_students:
            student_wrapper.reinitialize()
        for internship_offer_wrapper in self.offers_by_organization_speciality.values():
            internship_offer_wrapper.reinitialize()


def _get_valid_period(internship_offer_wrapper, student_wrapper, internship_offer):
    free_periods_name = internship_offer_wrapper.get_free_periods()
    random.shuffle(free_periods_name)
    student_periods_possible = \
        filter(lambda period: student_wrapper.has_period_assigned(period) is False,
               free_periods_name)
    enrollments_periods = student_wrapper.get_internships_periods(internship_offer_wrapper.internship_offer, internship_offer)
    if enrollments_periods:
        student_periods_possible = filter(lambda x: x in enrollments_periods, student_periods_possible)
    return next(student_periods_possible, None)


def is_permitted_offer(student_wrapper, internship_offer_wrapper):
    if internship_offer_wrapper.internship_offer.speciality.acronym in UNAUTHORIZED_SPECIALITIES:
        return False
    return True


def get_number_personal_offers(student_wrapper):
    # Si pas assez de choix pour les généralistes, assigne stage perso forcé
    assignments = student_wrapper.assignments
    number_personal_offers = 0
    for student_affectation in assignments.values():
        if student_affectation.organization.reference == str(REFERENCE_PERSONAL_ORGANIZATION):
            number_personal_offers += 1
    return number_personal_offers


def _occupy_offer(free_period_name, internship_offer_wrapper, student_wrapper, internship_choice, choice):
    period_places = internship_offer_wrapper.occupy(free_period_name)
    student_wrapper.assign(period_places.period, period_places.internship_offer.organization,
                           period_places.internship_offer.speciality, internship_choice, choice)


def _assign_offer_to_student(internship_offer_wrapper, internship_offer, preference, student_wrapper):
    free_period_name = _get_valid_period(internship_offer_wrapper, student_wrapper, internship_offer)
    if not free_period_name:
        return False
    _occupy_offer(free_period_name, internship_offer_wrapper, student_wrapper, internship_offer, preference)
    return True


def _load_internship_offers_and_places(cohort, periods):
    offers_by_organization_speciality = dict()
    period_ids = periods.values_list("id", flat=True)
    internships_periods_places = mdl_internship.period_internship_places.PeriodInternshipPlaces.objects.filter(period_id__in=period_ids)
    for period_places in filter_internships_period_places(internships_periods_places):
        internship_offer = period_places.internship_offer
        key = (internship_offer.organization.id, internship_offer.speciality.id)
        offers_by_organization_speciality[key] = offers_by_organization_speciality.get(key, InternshipOfferWrapper(internship_offer))
        offers_by_organization_speciality[key].set_period_places(period_places)
    return offers_by_organization_speciality


def filter_internships_period_places(internships_periods_places):
    return filter(lambda int_per_places: int_per_places.period.name.strip() in AUTHORIZED_PERIODS,
                  internships_periods_places)


def _load_students_and_choices(cohort):
    students_information_by_person_id = _load_student_information(cohort)
    students_by_registration_id = dict()
    student_choices = mdl_internship.internship_choice.get_internship_choices(cohort=cohort)
    for choice in student_choices:
        student = choice.student
        registration_id = student.registration_id
        students_by_registration_id[registration_id] = students_by_registration_id.get(registration_id, StudentWrapper(student))

        student_information = students_information_by_person_id.get(student.person.id, None)
        students_by_registration_id[registration_id].set_information(student_information)

        students_by_registration_id[registration_id].add_choice(choice)
    _load_student_enrollment(students_by_registration_id, cohort)
    return students_by_registration_id

def _load_student_information(cohort):
    students_information_by_person_id = dict()
    all_student_information = mdl_internship.internship_student_information.find_all(cohort=cohort)
    for student_information in all_student_information:
        students_information_by_person_id[student_information.person.id] = student_information
    return students_information_by_person_id

def _load_student_enrollment(students_by_registration_id, cohort):
    enrollments = mdl_internship.internship_enrollment.find_for_internships_for_cohort(cohort)
    for enrollment in enrollments:
        student_wrapper = students_by_registration_id.get(enrollment.student.registration_id, None)
        if student_wrapper:
            student_wrapper.add_enrollment(enrollment)

def _load_current_students_affectations(cohort):
    period_ids = mdl_internship.period.Period.objects.filter(cohort=cohort).values_list("id", flat=True)
    student_affectations = \
        mdl_internship.internship_student_affectation_stat.find_affectations(period_ids=period_ids)
    return filter(lambda stud_affectation: stud_affectation.period.name in AUTHORIZED_PERIODS,
                  student_affectations)

def _load_periods(cohort):
    periods = mdl_internship.period.Period.objects.filter(cohort=cohort)
    return list(filter(lambda period: period.name.strip() in AUTHORIZED_PERIODS, periods))

