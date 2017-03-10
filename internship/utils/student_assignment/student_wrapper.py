from internship import models as mdl_internship
from internship.utils.student_assignment.solver import NUMBER_INTERNSHIPS


class StudentWrapper:
    def __init__(self, student):
        self.student = student
        self.choices = []
        self.choices_by_preference = dict()
        self.assignments = dict()
        self.internship_assigned = []
        self.specialities_by_internship = dict()
        self.priority = False
        self.contest = "SS"
        self.cost = 0

    def add_choice(self, choice):
        self.choices.append(choice)
        self.__update_choices_by_preference(choice)
        self.__update_specialities_by_internship(choice)
        self.__update_priority(choice)

    def __update_priority(self, choice):
        if choice.priority:
            self.priority = True

    def __update_specialities_by_internship(self, choice):
        self.specialities_by_internship[choice.internship_choice] = choice.speciality

    def __update_choices_by_preference(self, choice):
        preference = choice.choice
        current_choices = self.choices_by_preference.get(preference, [])
        current_choices.append(choice)
        self.choices_by_preference[preference] = current_choices

    def assign(self, period, organization, speciality, internship_choice, preference):
        period_name = period.name
        cost = self.__get_cost(internship_choice, preference)
        self.cost += cost
        self.assignments[period_name] = \
            mdl_internship.internship_student_affectation_stat.\
            InternshipStudentAffectationStat(period=period, organization=organization, speciality=speciality,
                                             student=self.student, choice=preference, cost=cost)
        self.internship_assigned.append(internship_choice)

    def assign_specific(self, assignment):
        self.cost += assignment.cost
        period_name = assignment.period.name
        self.assignments[period_name] = assignment
        self.internship_assigned.append(0)

    def has_internship_assigned(self, internship):
        return internship in self.internship_assigned

    def has_all_internships_assigned(self):
        return len(self.internship_assigned) == NUMBER_INTERNSHIPS

    def get_choices_for_preference(self, preference):
        return self.choices_by_preference.get(preference, [])

    def has_period_assigned(self, period_name):
        return period_name in self.assignments

    def get_assignments(self):
        return self.assignments.values()

    def selected_specialities(self):
        return list(set([choice.speciality for choice in self.choices]))

    def fill_assignments(self, periods, default_organization, cost=0):
        if not self.choices:
            return
        for period in filter(lambda p: p.name not in self.assignments, periods):
            internship, speciality = self.get_internship_with_speciality_not_assigned()
            self.assign(period, default_organization, speciality, internship, cost)

    def get_internship_with_speciality_not_assigned(self):
        internships_with_speciality_not_assigned = \
            filter(lambda intern_spec: self.has_internship_assigned(intern_spec[0]) is False,
                   self.specialities_by_internship.items())
        return next(internships_with_speciality_not_assigned, (0, self.choices[0].speciality))

    @staticmethod
    def __get_cost(internship_choice, preference):
        if internship_choice == 0:
            return 10
        elif internship_choice == 5:
            return 5
        elif internship_choice == 6:
            return 10
        else:
            return preference - 1

    def reinitialize(self):
        self.assignments = dict()
        self.internship_assigned = []
        self.cost = 0