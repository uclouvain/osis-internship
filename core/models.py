from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.utils import timezone


class Person(models.Model):
    GENDER_CHOICES = (
        ('F','Female'),
        ('M','Male'),
        ('U','Unknown'))

    user        = models.OneToOneField(User, on_delete=models.CASCADE)
    middle_name = models.CharField(max_length = 50,blank = True, null = True)
    global_id   = models.CharField(max_length = 10,blank = True, null = True)
    gender      = models.CharField(max_length = 1, blank = True, null = True, choices = GENDER_CHOICES, default = 'U')
    national_id = models.CharField(max_length = 25,blank = True, null = True)

    def first_name(self):
        return self.user.first_name

    def last_name(self):
        return self.user.last_name

    def username(self):
        return self.user.username

    def __str__(self):
        return u"%s %s, %s" % (self.middle_name.upper(), self.user.last_name.upper(),self.user.first_name)


class Tutor(models.Model):
    person = models.ForeignKey(Person, null = False)

    def find_by_user(user):
        try:
            person = Person.objects.filter(user=user)
            tutor = Tutor.objects.get(person = person)
            return tutor
        except ObjectDoesNotExist:
            return None

    def __str__(self):
        return u"%s" % self.person


class Student(models.Model):
    registration_id = models.CharField(max_length=10, null=False)
    person          = models.ForeignKey(Person, null=False)

    def __str__(self):
        return u"%s (%s)" % (self.person, self.registration_id)


class Structure(models.Model):
    acronym = models.CharField(max_length=10, blank=False, null=False)
    title = models.TextField(blank=False, null=False)
    part_of = models.ForeignKey('self', blank=True, null=True)

    def __str__(self):
        return u"%s - %s" % (self.acronym, self.title)


class AcademicYear(models.Model):
    year = models.IntegerField(blank=False, null=False)

    def __str__(self):
        return u"%s-%s" % (self.year, self.year + 1)


class AcademicCalendar(models.Model):
    EVENT_TYPE = (
        ('academic_year', 'Academic Year'),
        ('session_exam_1', 'Session Exams 1'),
        ('session_exam_2', 'Session Exams 2'),
        ('session_exam_3', 'Session Exams 3'))

    academic_year = models.ForeignKey(AcademicYear, null = False)
    event_type    = models.CharField(max_length = 50, blank = False, null = False, choices = EVENT_TYPE)
    title         = models.CharField(max_length = 50, blank = True, null = True)
    description   = models.TextField(blank = True, null = True)
    start_date    = models.DateField(auto_now = False, blank = True, null = True, auto_now_add = False)
    end_date      = models.DateField(auto_now = False, blank = True, null = True, auto_now_add = False)

    def current_academic_year():
        academic_calendar = AcademicCalendar.objects.filter(event_type='academic_year').filter(start_date__lte=timezone.now()).filter(end_date__gte=timezone.now()).first()
        return academic_calendar.academic_year

    def __str__(self):
        return u"%s %s" % (self.academic_year, self.title)


class Offer(models.Model):
    acronym = models.CharField(max_length = 10,blank = False, null = False)
    title   = models.CharField(max_length = 255, blank = False, null = False)

    def save(self, *args, **kwargs):
        self.acronym = self.acronym.upper()
        super(Offer, self).save(*args, **kwargs)

    def __str__(self):
        return self.acronym


class OfferYear(models.Model):
    offer         = models.ForeignKey(Offer, null = False)
    academic_year = models.ForeignKey(AcademicYear, null = False)
    acronym       = models.CharField(max_length = 10,blank = False, null = False)
    title         = models.CharField(max_length = 255, blank = False, null = False)
    structure     = models.ForeignKey(Structure, null = True, blank = True)

    def __str__(self):
        return u"%s - %s" % (self.academic_year, self.offer.acronym)


class OfferEnrollment(models.Model):
    date_enrollment = models.DateField(auto_now = False, blank = False, null = False, auto_now_add = False)
    offer_year      = models.ForeignKey(OfferYear, null = False)
    student         = models.ForeignKey(Student, null = False)

    def __str__(self):
        return u"%s" % self.student


class OfferYearCalendar(models.Model):
    EVENT_TYPE = (
        ('session_exam_1','Session Exams 1'),
        ('session_exam_2','Session Exams 2'),
        ('session_exam_3','Session Exams 3'))

    academic_calendar = models.ForeignKey(AcademicCalendar, null = False)
    event_type        = models.CharField(max_length = 50, blank = False, null = False, choices = EVENT_TYPE)
    start_date        = models.DateField(auto_now = False, blank = True, null = True, auto_now_add = False)
    end_date          = models.DateField(auto_now = False, blank = True, null = True, auto_now_add = False)

    def current_session_exam():
        return OfferYearCalendar.objects.filter(event_type__startswith='session_exam').filter(start_date__lte=timezone.now()).filter(end_date__gte=timezone.now()).first()

    def __str__(self):
        return u"%s" % self.academic_calendar


class LearningUnit(models.Model):
    acronym     = models.CharField(max_length = 10, blank = False, null = False)
    title       = models.CharField(max_length = 255, null = False)
    description = models.TextField(blank = True, null = True)
    start_year  = models.IntegerField(blank = False, null = False)
    end_year    = models.IntegerField(blank = True, null = True)

    def __str__(self):
        return u"%s - %s" % (self.acronym, self.title)


class LearningUnitYear(models.Model):
    acronym       = models.CharField(max_length = 10,blank = False, null = False)
    title         = models.CharField(max_length = 255, blank = False, null = False)
    credits       = models.DecimalField(max_digits = 4, decimal_places = 2, blank = True, null = True)
    academic_year = models.ForeignKey(AcademicYear, null = True)
    learning_unit = models.ForeignKey(LearningUnit, null = True)

    def __str__(self):
        return u"%s - %s" % (self.academic_year,self.learning_unit)


class LearningUnitEnrollment(models.Model):
    date_enrollment    = models.DateField(auto_now = False, blank = False, null = False, auto_now_add = False)
    learning_unit_year = models.ForeignKey(LearningUnitYear, null = False)
    offer_enrollment   = models.ForeignKey(OfferEnrollment, null = False)

    def student(self):
        return self.offer_enrollment.student

    def __str__(self):
        return u"%s - %s" % (self.learning_unit_year, self.offer_enrollment.student)


class Attribution(models.Model):
    FUNCTION_CHOICES = (
        ('COORDINATOR','Coordinator'),
        ('PROFESSOR','Professor'))

    start_date    = models.DateField(auto_now = False, blank = True, null = True, auto_now_add = False)
    end_date      = models.DateField(auto_now = False, blank = True, null = True, auto_now_add = False)
    function      = models.CharField(max_length = 15, blank = True, null = True,choices = FUNCTION_CHOICES, default = 'UNKNOWN')
    learning_unit = models.ForeignKey(LearningUnit, null = False)
    tutor         = models.ForeignKey(Tutor, null = False)

    def __str__(self):
        return u"%s - %s" % (self.tutor.person, self.function)


class SessionExam(models.Model):
    SESSION_STATUS = (
        ('IDLE', 'Idle'),
        ('OPEN', 'Open'),
        ('CLOSED', 'Closed'))

    number_session      = models.IntegerField(blank = False, null = False)
    status              = models.CharField(max_length = 10, blank = False, null = False,choices = SESSION_STATUS)
    learning_unit_year  = models.ForeignKey(LearningUnitYear, null = False)
    offer_year_calendar = models.ForeignKey(OfferYearCalendar, blank = False, null = True)

    def current_session_exam():
        offer_calendar = OfferYearCalendar.current_session_exam()
        session_exam = SessionExam.objects.filter(offer_year_calendar=offer_calendar).first()
        return session_exam

    def find_session(id):
        return SessionExam.objects.get(pk=1)

    def sessions(tutor, academic_year, session):
        learning_units = Attribution.objects.filter(tutor=tutor).values('learning_unit')
        return SessionExam.objects.filter(number_session=session.number_session
                                 ).filter(learning_unit_year__academic_year=academic_year
                                 ).filter(learning_unit_year__learning_unit__in=learning_units)

    def __str__(self):
        return u"%s - %d" % (self.learning_unit_year, self.number_session)


class ExamEnrollment(models.Model):
    JUSTIFICATION_TYPES = (
        ('ABSENT','Absent'),
        ('CHEATING','Cheating'),
        ('ILL','Ill'),
        ('JUSTIFIED_ABSENCE','Justified absence'),
        ('SCORE_MISSING','Score missing'))

    ENCODING_STATUS = (
        ('SAVED','Saved'),
        ('SUBMITTED','Submitted'))

    score                    = models.DecimalField(max_digits = 4, decimal_places = 2, blank = True, null = True, validators=[MaxValueValidator(20), MinValueValidator(0)])
    justification            = models.CharField(max_length = 17, blank = True, null = True,choices = JUSTIFICATION_TYPES)
    encoding_status          = models.CharField(max_length = 9, blank = True, null = True,choices = ENCODING_STATUS)
    session_exam             = models.ForeignKey(SessionExam, null = False)
    learning_unit_enrollment = models.ForeignKey(LearningUnitEnrollment, null = False)

    def calculate_progress(enrollments):
        return len([e for e in enrollments if e.score is not None or e.justification is not None]) / len(enrollments)

    def find_exam_enrollments(session_exam):
        return ExamEnrollment.objects.filter(session_exam=session_exam)
