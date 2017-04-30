import csv
import sys
import operator
import uuid
from internship.models.internship_choice import InternshipChoice

class InternshipChoiceSynchronizer:
    def __init__(self, choices_file):
        self.choices_file = choices_file

    def run(self):
        with open(self.choices_file, 'rt') as csvfile:
            rows = csv.reader(csvfile)
            next(rows, None)
            uuids = list(map(lambda x: x[-1], rows))
            self.sync_choices_by_uuids(uuids)

    def sync_choices_by_uuids(self, uuids):
        print("%s choices to sync..." % len(uuids))
        choices_to_destroy = InternshipChoice.objects.exclude(uuid__in=uuids).all()
        print("About to delete %s choices. This cannot be reversed. Are you sure?" % len(choices_to_destroy))
        while True:
            confirm = input('[c]continue or [x]exit: ')
            if confirm == 'c':
                print("Deleting %s out-of-sync choices..." % len(choices_to_destroy))
                choices_to_destroy.delete()
                print("Done")
                return confirm
            elif confirm == 'x':
                print("Got it! Come back when your mind is made up.")
                break
            else:
                print("Invalid Option. Please Enter a Valid Option.")
