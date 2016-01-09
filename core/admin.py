from django.contrib import admin

from .models import AcademicYear
from .models import AcademicCalendar
from .models import Attribution
from .models import SessionExam
from .models import ExamEnrollment
from .models import LearningUnit
from .models import LearningUnitEnrollment
from .models import LearningUnitYear
from .models import Offer
from .models import OfferEnrollment
from .models import OfferYear
from .models import OfferYearCalendar
from .models import Structure
from .models import Person
from .models import ProgrammeManager
from .models import Student
from .models import Tutor

admin.site.register(AcademicYear)

class AcademicCalendarAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_type', 'academic_year', 'start_date', 'end_date')

admin.site.register(AcademicCalendar, AcademicCalendarAdmin)

class OfferAdmin(admin.ModelAdmin):
    list_display = ('acronym','title')

admin.site.register(Offer, OfferAdmin)

class OfferYearAdmin(admin.ModelAdmin):
    list_display = ('offer','academic_year')

admin.site.register(OfferYear, OfferYearAdmin)

class OfferCalendarAdmin(admin.ModelAdmin):
    list_display = ('academic_calendar', 'event_type', 'start_date', 'end_date')

admin.site.register(OfferYearCalendar, OfferCalendarAdmin)

class OfferEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('offer_year','student', 'date_enrollment')

admin.site.register(OfferEnrollment, OfferEnrollmentAdmin)

class PersonAdmin(admin.ModelAdmin):
    list_display = ('first_name' , 'middle_name', 'last_name', 'username', 'gender','global_id', 'national_id')

admin.site.register(Person, PersonAdmin)

class LearningUnitAdmin(admin.ModelAdmin):
    list_display = ('acronym', 'title', 'start_year', 'end_year')

admin.site.register(LearningUnit, LearningUnitAdmin)

class LearningUnitYearAdmin(admin.ModelAdmin):
    list_display = ('acronym', 'title', 'academic_year', 'credits')

admin.site.register(LearningUnitYear, LearningUnitYearAdmin)

class LearningUnitEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'learning_unit_year', 'date_enrollment')

admin.site.register(LearningUnitEnrollment, LearningUnitEnrollmentAdmin)

class SessionExamAdmin(admin.ModelAdmin):
    list_display = ('learning_unit_year', 'number_session', 'status')

admin.site.register(SessionExam, SessionExamAdmin)

class ExamEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('learning_unit_enrollment', 'session_exam', 'score', 'justification', 'encoding_status')

admin.site.register(ExamEnrollment, ExamEnrollmentAdmin)

class StructureAdmin(admin.ModelAdmin):
    list_display = ('acronym', 'title', 'part_of')

admin.site.register(Structure, StructureAdmin)

class StudentAdmin(admin.ModelAdmin):
    list_display = ('person', 'registration_id')

admin.site.register(Student, StudentAdmin)
admin.site.register(Tutor)

class ProgrammeManagerAdmin(admin.ModelAdmin):
    list_display = ('person', 'faculty')

admin.site.register(ProgrammeManager, ProgrammeManagerAdmin)

class AttributionAdmin(admin.ModelAdmin):
    list_display = ('tutor','function','learning_unit','start_date', 'end_date')

admin.site.register(Attribution, AttributionAdmin)
