
class PersonAddress(models.Model):
    person      = models.ForeignKey(Person)
    label       = models.CharField(max_length=20)
    location    = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=20)
    city        = models.CharField(max_length=255)
    country     = models.CharField(max_length=255)
