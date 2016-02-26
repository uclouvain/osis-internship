

class Student(models.Model):
    external_id     = models.CharField(max_length=100, blank=True, null=True)
    changed         = models.DateTimeField(null=True)
    registration_id = models.CharField(max_length=10)
    person          = models.ForeignKey(Person)

    def __str__(self):
        return u"%s (%s)" % (self.person, self.registration_id)