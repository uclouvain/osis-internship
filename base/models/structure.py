class Structure(models.Model):
    external_id  = models.CharField(max_length=100, blank=True, null=True)
    changed      = models.DateTimeField(null=True)
    acronym      = models.CharField(max_length=15)
    title        = models.CharField(max_length=255)
    organization = models.ForeignKey(Organization, null=True)
    part_of      = models.ForeignKey('self', null=True, blank=True)

    @staticmethod
    def find_structures():
        return Structure.objects.all().order_by('acronym')

    @staticmethod
    def find_by_id(id):
        return Structure.objects.get(pk=id)

    def find_children(self):
        return Structure.objects.filter(part_of=self).order_by('acronym')

    def find_offer_years_by_academic_year(self):
        return OfferYear.objects.filter(structure=self).order_by('academic_year','acronym')

    def __str__(self):
        return u"%s - %s" % (self.acronym, self.title)