from datetime import datetime, timedelta
from random import randint

from django.db import migrations
from django.db.migrations import RunPython


def populate_internship_choices(apps, schema_editor):
    Student = apps.get_model('base', 'Student')
    Organization = apps.get_model('internship', 'Organization')
    InternshipSpeciality = apps.get_model('internship', 'InternshipSpeciality')
    Internship = apps.get_model('internship', 'Internship')
    InternshipChoice = apps.get_model('internship', 'InternshipChoice')
    InternshipStudentInformation = apps.get_model('internship', 'InternshipStudentInformation')

    # Obtenez tous les étudiants, organisations, spécialités de stage, stages

    students_infos = InternshipStudentInformation.objects.filter(cohort__name='R6-2026 M1')
    students = Student.objects.filter(person_id__in=[s.person_id for s in students_infos])
    organizations = Organization.objects.filter(cohort__name='R6-2026 M1')
    specialities = InternshipSpeciality.objects.filter(cohort__name='R6-2026 M1')

    mandatory_internships = Internship.objects.filter(cohort__name='R6-2026 M1', speciality__isnull=False)
    non_mandatory_internships = Internship.objects.filter(cohort__name='R6-2026 M1', speciality__isnull=True)

    InternshipChoice.objects.filter(internship__cohort__name='R6-2026 M1').delete()

    for internship in mandatory_internships:
        for student in students:
            for choice in range(1, 5):
                organization = organizations[randint(0, organizations.count() - 1)]
                # Créez un choix de stage pour l'étudiant
                InternshipChoice.objects.create(
                    student=student,
                    organization=organization,
                    speciality=internship.speciality,
                    choice=choice,
                    internship=internship,
                    priority=False,
                )

    for internship in non_mandatory_internships:
        for student in students:
            for choice in range(1, 5):
                organization = organizations[randint(0, organizations.count() - 1)]
                speciality = specialities[randint(0, specialities.count() - 1)]
                # Créez un choix de stage pour l'étudiant
                InternshipChoice.objects.create(
                    student=student,
                    organization=organization,
                    speciality=speciality,
                    choice=choice,
                    internship=internship,
                    priority=False,
                )


class Migration(migrations.Migration):

    dependencies = [
        ('internship', '0033_period_exclude_from_assignment'),
    ]

    operations = [
        migrations.RunPython(populate_internship_choices, reverse_code=RunPython.noop),
    ]
