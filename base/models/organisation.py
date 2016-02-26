class Organization(models.Model):
    external_id = models.CharField(max_length=100, blank=True, null=True)
    changed     = models.DateTimeField(null=True)
    name        = models.CharField(max_length=255)
    acronym     = models.CharField(max_length=15)
    website     = models.CharField(max_length=255, blank=True, null=True)
    reference   = models.CharField(max_length=30, blank=True, null=True)

    def __str__(self):
        return self.name