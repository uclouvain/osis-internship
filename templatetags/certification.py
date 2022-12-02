from django.template.defaulttags import register
from django.utils import formats
from django.utils.datetime_safe import date
from django.utils.translation import gettext as _

from internship.models.internship_certifier import InternshipCertifier


@register.inclusion_tag('signature.html')
def get_certification():
    current_date = formats.date_format(date.today(), use_l10n=True)
    return {
        'certification_text': _("Certified in conformity with registered evaluations. Brussels, {}.").format(
            current_date
        ),
        'certifiers': InternshipCertifier.objects.all()
    }
