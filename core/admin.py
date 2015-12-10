from django.contrib import admin

from .models import AcademicYear
from .models import Attribution
from .models import SessionExam
from .models import ExamEnrollment
from .models import LearningUnit
from .models import LearningUnitEnrollment
from .models import LearningUnitYear
from .models import Offer
from .models import OfferEnrollment
from .models import OfferYear
from .models import Structure
from .models import Person
from .models import Student
from .models import Tutor

class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ('year', 'start_date', 'end_date')

class AttributionAdmin(admin.ModelAdmin):
    list_display = ('tutor','function','start_date', 'end_date')

class OfferAdmin(admin.ModelAdmin):
    list_display = ('acronym','title')

class PersonAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'middle_name', 'last_name', 'gender','global_id', 'national_number')

class OfferYearAdmin(admin.ModelAdmin):
    list_display = ('offer','academic_year')

admin.site.register(Structure)
admin.site.register(AcademicYear, AcademicYearAdmin)
admin.site.register(Offer, OfferAdmin)
admin.site.register(OfferYear, OfferYearAdmin)
admin.site.register(LearningUnit)
admin.site.register(LearningUnitYear)
admin.site.register(Person, PersonAdmin)
admin.site.register(Student)
admin.site.register(Tutor)
admin.site.register(Attribution, AttributionAdmin)
admin.site.register(SessionExam)
admin.site.register(ExamEnrollment)
admin.site.register(LearningUnitEnrollment)
admin.site.register(OfferEnrollment)
