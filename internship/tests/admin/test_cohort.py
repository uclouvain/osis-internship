from django.contrib.auth.models import Permission, User
from django.core.urlresolvers import reverse
from django.test import TestCase

from internship.tests.utils.test_student_loader import create_csv_stream
from internship.tests.factories.cohort import CohortFactory


class CohortAdminTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('demo', 'demo@demo.org', 'passtest', is_staff=True, is_superuser=True)
        permission = Permission.objects.get(codename='is_internship_manager')
        self.user.user_permissions.add(permission)
        self.user.save()

    def test_cohort_simple_get(self):
        cohort = CohortFactory()

        self.client.force_login(self.user)

        url = reverse('admin:cohort-import-students',
                      kwargs={'cohort_id': cohort.id})

        response = self.client.get(url)

        self.assertTemplateUsed(response,
                                'admin/internship/cohort/import_students.html')

    def test_cohort_upload_csv_file(self):
        cohort = CohortFactory()

        self.client.force_login(self.user)
        url = reverse('admin:cohort-import-students',
                      kwargs={
                          'cohort_id': cohort.id,
                      })

        with create_csv_stream('demo.csv') as str_io:
            response = self.client.post(url, {'file_upload': str_io})
            cohort_url = reverse('admin:internship_cohort_change',
                                 args=[cohort.id])
            self.assertRedirects(response, cohort_url)
