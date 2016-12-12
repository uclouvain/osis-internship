import csv
from django.db import IntegrityError
from base import models as mdl


# To be removed once all program managers are imported.
def load_program_managers():
    with open('program-managers.csv') as csvfile:
        row = csv.reader(csvfile)
        imported_counter = 0
        error_counter = 0
        duplication_counter = 0
        for columns in row:
            if len(columns) > 0:
                offer_years = mdl.offer_year.find_by_acronym(columns[0].strip())
                person = mdl.person.find_by_global_id(columns[2].strip())

                if offer_years:
                    if person:
                        for offer_year in offer_years:
                            program_manager = mdl.program_manager.ProgramManager()
                            program_manager.offer_year = offer_year
                            program_manager.person = person
                            try:
                                program_manager.save()
                                print('Saved : %s - %s' % (offer_year, person))
                                imported_counter += 1
                            except IntegrityError:
                                print('Duplicated : %s - %s' % (offer_year, person))
                                duplication_counter += 1
                    else:
                        error_counter += 1
                        print(u'No person named "%s" for "%s", "%s", "%s"' % (person, columns[0], columns[1], columns[2]))
                else:
                    error_counter += 1
                    print(u'No offer year named "%s" for "%s", "%s", "%s"' % (columns[0], columns[1], columns[2], person))
        print(u'%d program managers imported.' % imported_counter)
        print(u'%d program managers not imported.' % error_counter)
        print(u'%d program managers duplicated.' % duplication_counter)
