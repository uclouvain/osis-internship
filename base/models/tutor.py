class Tutor(models.Model):
    external_id = models.CharField(max_length=100, blank=True, null=True)
    changed     = models.DateTimeField(null=True)
    person      = models.ForeignKey(Person)

    @staticmethod


    def __str__(self):
        return u"%s" % self.person


def find_by_user(user):
    try:
        person = Person.find_person_by_user(user)
        # tutor = Tutor.objects.filter(person=person)
        tutor = Tutor.objects.get(person = person)

        return tutor
    except ObjectDoesNotExist:
        return None