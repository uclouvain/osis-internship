from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse

from openpyxl import Workbook
from openpyxl.writer.excel import save_virtual_workbook
from openpyxl.cell import get_column_letter
from openpyxl import load_workbook

from core.models import AcademicCalendar, SessionExam, ExamEnrollment, LearningUnitYear, Person, AcademicYear, Student,OfferYear,LearningUnitEnrollment,OfferEnrollment
from core.forms import ScoreFileForm

@login_required
def upload_scores_file(request):
    print ('upload_scores_file')
    """

    :param request:
    :return:
    """
    if request.method == 'POST':
        form = ScoreFileForm(request.POST, request.FILES)
        if form.is_valid():
            print ('form valid')
            __save_xls_scores(request.FILES['file'])
            return HttpResponseRedirect(reverse('scores_encoding'))


def __save_xls_scores(file):
    print('save_xls_scores')
    wb = load_workbook(file, read_only=True)
    ws = wb.active
    nb_row = 0
    isValid = False
    for row in ws.rows:
        if nb_row > 0 and isValid:
            student = Student.objects.get(registration_id=row[5].value)
            academic_year = AcademicYear.objects.get(year=int(row[0].value[:4]))
            offer_year = OfferYear.objects.get(academic_year=academic_year,acronym=row[3].value)
            offer_enrollment = OfferEnrollment.objects.get(student=student,offer_year=offer_year)
            learning_unit_year = LearningUnitYear.objects.get(academic_year=academic_year,acronym=row[2].value)
            learning_unit_enrollment = LearningUnitEnrollment.objects.get(learning_unit_year=learning_unit_year,offer_enrollment=offer_enrollment)
            exam_enrollment = ExamEnrollment.objects.filter(learning_unit_enrollment = learning_unit_enrollment).filter(session_exam__number_session = int(row[1].value)).first()
            exam_enrollment.score = float(row[8].value)
            exam_enrollment.save()
        else:
            #todo
            #Il faut valider le fichier xls
            isValid = True
        nb_row = nb_row + 1;
