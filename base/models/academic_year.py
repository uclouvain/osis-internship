class AcademicYear(models.Model):
    external_id = models.CharField(max_length=100, blank=True, null=True)
    changed     = models.DateTimeField(null=True)
    year        = models.IntegerField()

    @staticmethod
    def find_academic_year(id):
        return AcademicYear.objects.get(pk=id)

    @staticmethod
    def find_academic_years():
        return AcademicYear.objects.all().order_by('year')

    def __str__(self):
        return u"%s-%s" % (self.year, self.year + 1)