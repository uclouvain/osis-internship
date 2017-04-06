from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import ugettext_lazy as _

from internship.forms.cohort import CohortForm
from internship.models.cohort import Cohort


@login_required()
@permission_required('internship.is_internship_manager', raise_exception=True)
def new(request):
    form = CohortForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect(reverse('internship'))

    context = {
        'form': form,
        'page_title': _('create_cohort'),
    }
    return render(request, 'cohort/cohort_form.html', context)


@login_required()
@permission_required('internship.is_internship_manager', raise_exception=True)
def edit(request, cohort_id):
    cohort = get_object_or_404(Cohort, pk=cohort_id)

    form = CohortForm(data=request.POST or None, instance=cohort)

    if form.is_valid():
        form.save()
        return redirect(reverse('internship'))

    context = {
        'form': form,
        'page_title': _('edit_cohort'),
    }

    return render(request, 'cohort/cohort_form.html', context)