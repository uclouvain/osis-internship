from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User
import datetime

class Person(models.Model):
    GENDER_CHOICES = (
        ('F','Female'),
        ('M','Male'),
        ('U','Unknown'))

    user            = models.OneToOneField(User, on_delete=models.CASCADE)
    middle_name     = models.CharField(max_length = 50,blank = True, null = True)
    global_id       = models.CharField(max_length = 10,blank = True, null = True)
    gender          = models.CharField(max_length = 1, blank = True, null = True, choices = GENDER_CHOICES, default = 'U')
    national_number = models.CharField(max_length = 25,blank = True, null = True)

    def first_name(self):
        return self.user.first_name

    def last_name(self):
        return self.user.last_name

    def username(self):
        return self.user.username

    def __str__(self):
        return u"%s %s %s" % (self.middle_name.upper(), self.user.last_name.upper(),self.user.first_name)


class Tutor(models.Model):
    person = models.ForeignKey(Person, null = False)

    def __str__(self):
        return u"%s" % (self.person)


class Student(models.Model):
    registration_number = models.CharField(max_length = 10, null = False)
    person              = models.ForeignKey(Person, null = False)

    def __str__(self):
        return u"%s (%s)" % (self.person, self.registration_number)


class Structure(models.Model):
    title = models.TextField(blank = False, null = False)

    def __str__(self):
        return str(self.title)


class AcademicYear(models.Model):
    year       = models.IntegerField(blank = False, null = False)
    start_date = models.DateField(auto_now = False, blank = True, null = True, auto_now_add = False)
    end_date   = models.DateField(auto_now = False, blank = True, null = True, auto_now_add = False)

    def __str__(self):
        return u"%s-%s" % (self.year, self.year + 1)


class Offer(models.Model):
    acronym = models.CharField(max_length = 10,blank = False, null = False)
    title   = models.CharField(max_length = 255, blank = False, null = False)

    def __str__(self):
        return self.acronym.upper()

    def save(self, *args, **kwargs):
        self.acronym = self.acronym.upper()
        super(Offer, self).save(*args, **kwargs)


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
    description   = models.TextField(blank = True, null = True)
    credits       = models.DecimalField(max_digits = 4, decimal_places = 2, blank = True, null = True)
    academic_year = models.ForeignKey(AcademicYear, null = True)
    learning_unit = models.ForeignKey(LearningUnit, null = True)

    def __str__(self):
        return u"%s - %s" % (self.academic_year,self.learning_unit)


class OfferYear(models.Model):
    offer          = models.ForeignKey(Offer, null = False)
    academic_year  = models.ForeignKey(AcademicYear, null = False)
    structure      = models.ForeignKey(Structure, null = True, blank = True)

    def __str__(self):
        return u"%s - %s" % (self.academic_year, self.offer.acronym)


class OfferEnrollment(models.Model):
    date_enrollment = models.DateField(auto_now = False, blank = False, null = False, auto_now_add = False)
    offer_year      = models.ForeignKey(OfferYear, null = False)
    student         = models.ForeignKey(Student, null = False)

    def __str__(self):
        return u"%s - %s" % (self.offer_year, self.student)


class LearningUnitEnrollment(models.Model):
    date_enrollment    = models.DateField(auto_now = False, blank = False, null = False, auto_now_add = False)
    learning_unit_year = models.ForeignKey(LearningUnitYear, null = False)
    offer_enrollment   = models.ForeignKey(OfferEnrollment, null = False)

    def __str__(self):
        return u"%s - %s - %s - %s" % (self.learning_unit_year.academic_year.year,
                                       self.learning_unit_year.title,
                                       self.offer_enrollment.offer_year.offer.acronym,
                                       self.offer_enrollment.student.person.last_name)


class SessionExam(models.Model):
    GENDER_CHOICES = (
        ('CLS','Closed'),
        ('OPN','Open'),
        ('U','Unknown'))

    date_session       = models.DateField(auto_now = False, blank = False, null = False, auto_now_add = False)
    status             = models.BooleanField(default = False)
    learning_unit_year = models.ForeignKey(LearningUnitYear, null = False)

    @property
    def session_name(self):
        if self.date_session:
            return self.date_session.strftime("%B")
        return ""


    def __str__(self):
        name_build = ''
        if self.learning_unit_year:
            name_build += str(self.learning_unit_year.academic_year.year)
            if self.learning_unit_year.title:
                name_build+= ' - '
                name_build += self.learning_unit_year.title
            if self.session_name:
                name_build+= ' - '
                name_build += self.session_name
        return name_build


class ExamEnrollment(models.Model):
    JUSTIFICATION_CHOICES = (
        ('ABSENT','Absent'),
        ('CHEATING','Cheating'),
        ('ILL','Ill'),
        ('JUSTIFIED_ABSENCE','Justified absence'),
        ('SCORE_MISSING','Score missing'))

    ENCODING_STATUS_CHOICES = (
        ('SAVED','Saved'),
        ('SUBMITTED','Submitted'))

    score                    = models.DecimalField(max_digits = 4, decimal_places = 2, blank = True, null = True, validators=[
                                        MaxValueValidator(20),
                                        MinValueValidator(0)])
    justification            = models.CharField(max_length = 17, blank = True, null = True,choices = JUSTIFICATION_CHOICES)
    encoding_status          = models.CharField(max_length = 9, blank = True, null = True,choices = ENCODING_STATUS_CHOICES)
    session_exam             = models.ForeignKey(SessionExam, null = False)
    learning_unit_enrollment = models.ForeignKey(LearningUnitEnrollment, null = False)


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
