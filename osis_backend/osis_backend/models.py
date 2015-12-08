from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
import datetime

class Structure(models.Model):
    title = models.TextField(blank = True, null = True)

    def offer_years(self):
        return OfferYear.objects.filter(structure=self)

    def __str__(self):
        return str(self.title)


class AcademicYear(models.Model):
    year       = models.IntegerField(validators=[
                                        MaxValueValidator(3000),
                                        MinValueValidator(1967)
                                        ],
                                      blank = False, null = False
                                     )
    start_date = models.DateField(auto_now = False, blank = True, null = True, auto_now_add = False)
    end_date   = models.DateField(auto_now = False, blank = True, null = True, auto_now_add = False)

    def offer_years(self):
        return OfferYear.objects.filter(academic_year=self)
    def learning_unit_years(self):
        return LearningUnitYear.objects.filter(academic_year=self)

    def __str__(self):
        return str(self.year)


class LearningUnit(models.Model):
    start_year = models.IntegerField(validators=[
                                        MaxValueValidator(3000),
                                        MinValueValidator(1967)
                                        ], blank = False, null = False
                                     )
    end_year   = models.IntegerField(validators=[
                                        MaxValueValidator(3000),
                                        MinValueValidator(1967)
                                        ], blank = False, null = False
                                     )
    def learning_unit_years(self):
        return LearningUnitYear.objects.filter(learning_unit=self)
    def attributions(self):
        return Attribution.objects.filter(learning_unit=self)

    def __str__(self):
        return u"%s - %s" % (str(self.start_year), str(self.end_year))


class LearningUnitYear(models.Model):
    acronym       = models.CharField(max_length = 5,blank = False, null = False)
    title         = models.TextField(blank = True, null = True)
    credits       = models.DecimalField(max_digits = 4, decimal_places = 2, blank = True, null = True)

    academic_year = models.ForeignKey(AcademicYear, null = True)
    learning_unit = models.ForeignKey(LearningUnit, null = True)

    def learning_unit_enrollments(self):
        return LearningUnitEnrollment.objects.filter(learning_unit_year=self)
    def session_exams(self):
        return SessionExam.objects.filter(learning_unit_year=self)

    def __str__(self):
        return u"%s - %s" % (self.acronym,self.title)


class Offer(models.Model):
    acronym = models.CharField(max_length = 10,blank = False, null = False)
    title   = models.TextField(blank = False, null = False)

    def offer_years(self):
        return OfferYear.objects.filter(offer=self)
    def offer_enrollments(self):
        return OfferEnrollment.objects.filter(offer=self)

    def __str__(self):
        return self.acronym.upper()

    def save(self, *args, **kwargs):
        self.acronym = self.acronym.upper()
        super(Offer, self).save(*args, **kwargs)


class OfferYear(models.Model):
    offer          = models.ForeignKey(Offer, null = True)
    academic_year  = models.ForeignKey(AcademicYear, null = True)
    structure      = models.ForeignKey(Structure, null = True)

    @property
    def offer_acronym(self):
        if self.offer:
            return self.offer.acronym
        return ""

    @property
    def academic_year_year(self):
        if self.academic_year:
            return str(self.academic_year.year)
        return ""

    def __str__(self):
        acronym = u"%s" % self.offer.acronym
        year = u"%s" % self.academic_year.year
        return u"%s - %s" % (acronym,year)


class Person(models.Model):
    GENDER_CHOICES = (
        ('F','Female'),
        ('M','Male'),
        ('U','Unknown')
    )

    last_name       = models.CharField(max_length = 50,blank = True, null = True)
    first_name      = models.CharField(max_length = 50,blank = True, null = True)
    middle_name     = models.CharField(max_length = 50,blank = True, null = True)
    global_id       = models.CharField(max_length = 10,blank = True, null = True)
    gender          = models.CharField(max_length = 1, blank = True, null = True,choices = GENDER_CHOICES, default = 'U')
    national_number = models.CharField(max_length = 25,blank = True, null = True)

    @property
    def name(self):
        return ''.join(
            [self.last_name,' ,', self.first_name])

    def __str__(self):
        return u"%s - %s" % (self.last_name,self.first_name)


class Student(models.Model):
    registration_number = models.CharField(max_length = 10, blank = True, null = True)

    person              = models.ForeignKey(Person, null = True)

    def offer_enrollments(self):
        return OfferEnrollment.objects.filter(student=self)

    def __str__(self):
        return u"%s (%s)" % (self.person.name,self.registration_number)


class OfferEnrollment(models.Model):
    date_enrollment = models.DateField(auto_now = False, blank = True, null = True, auto_now_add = False)
    offer_year      = models.ForeignKey(OfferYear)
    student         = models.ForeignKey(Student)

    def learning_unit_enrollments(self):
        return LearningUnitEnrollment.objects.filter(offer_enrollment=self)

    def __str__(self):
        offer_acronym = u"%s" % self.offer_year.offer.acronym
        offer_title = u"%s" % self.offer_year.offer.title
        offer_year = u"%s" % self.offer_year.academic_year.year
        student = u"%s" % self.student.person.last_name
        return u"%s - %s - %s - %s" % (offer_acronym,offer_title,offer_year,student)


class LearningUnitEnrollment(models.Model):
    date_enrollment    = models.DateField(auto_now = False, blank = True, null = True, auto_now_add = False)

    learning_unit_year = models.ForeignKey(LearningUnitYear, null = False)
    offer_enrollment   = models.ForeignKey(OfferEnrollment, null = False)

    def exam_enrollments(self):
        return ExamEnrollment.objects.filter(learning_unit_enrollment=self)

    def __str__(self):
        year = u"%s" % self.learning_unit_year.academic_year.year
        title = u"%s" % self.learning_unit_year.title
        offer_acronym = u"%s" % self.offer_enrollment.offer_year.offer.acronym
        student = u"%s" % self.offer_enrollment.student.person.last_name
        return u"%s - %s - %s - %s" % (year,title,offer_acronym,student)


class SessionExam(models.Model):
    date_session       = models.DateField(auto_now = False, blank = True, null = True, auto_now_add = False)
    closed             = models.BooleanField(default = False)

    learning_unit_year = models.ForeignKey(LearningUnitYear, null = True)

    @property
    def session_name(self):
        if self.date_session:
            return self.date_session.strftime("%B")
        return ""

    def exam_enrollments(self):
        return ExamEnrollment.objects.filter(session_exam=self)

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
        ('ILL','Ill'),
        ('ABSENT','Absent'),
        ('JUSTIFIED_ABSENCE','Justified absence'),
        ('CHEATING','Cheating'),
        ('SCORE_MISSING','Score missing')
    )
    ENCODING_STATUS_CHOICES = (
        ('SAVED','Saved'),
        ('SUBMITTED','Submitted')
    )

    score                    = models.DecimalField(max_digits = 4, decimal_places = 2, blank = True, null = True, validators=[
                                        MaxValueValidator(20),
                                        MinValueValidator(0)
                                        ])
    justification            = models.CharField(max_length = 17, blank = True, null = True,choices = JUSTIFICATION_CHOICES)
    encoding_status          = models.CharField(max_length = 9, blank = True, null = True,choices = ENCODING_STATUS_CHOICES)

    session_exam             = models.ForeignKey(SessionExam, null = True)
    learning_unit_enrollment = models.ForeignKey(LearningUnitEnrollment, null = True)


class Tutor(models.Model):
    person = models.ForeignKey(Person, null = True)

    def attributions(self):
        return Attribution.objects.filter(tutor=self)

    def __str__(self):
        return u"%s" % (self.person.name)


class Attribution(models.Model):
    FUNCTION_CHOICES = (
        ('UNKNOWN','Unknown'),
        ('PROFESSOR','Professor'),
        ('COORDINATOR','Coordinator')
    )

    start_date    = models.DateField(auto_now = False, blank = True, null = True, auto_now_add = False)
    end_date      = models.DateField(auto_now = False, blank = True, null = True, auto_now_add = False)
    function      = models.CharField(max_length = 15, blank = True, null = True,choices = FUNCTION_CHOICES, default = 'UNKNOWN')

    learning_unit = models.ForeignKey(LearningUnit, null = True)
    tutor         = models.ForeignKey(Tutor, null = True)

    @property
    def teacher(self):
        if self.tutor:
            return self.tutor.person.name
        return ""

    def __str__(self):
        return u"%s - %s" % (self.tutor.person.name, self.function)
