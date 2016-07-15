##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2016 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from base import models as mdl
from internship.models import InternshipOffer, InternshipStudentInformation, OrganizationAddress
import urllib.request
import unicodedata
from xml.dom import minidom

@login_required
@permission_required('internship.can_access_internship', raise_exception=True)
def internships_home(request):
    student = mdl.student.find_by(person_username=request.user)
    #Check if the user is a student, if not the noma is not requiered so it's 0
    if len(student) > 0:
        for s in student:
            noma = s.registration_id
    else:
        noma = 0

    internships = InternshipOffer.find_internships()
    #Check if there is a internship offers in data base. If not, the internships
    #can be block, but there is no effect
    if len(internships) > 0:
        if internships[0].selectable:
            blockable = True
        else:
            blockable = False
    else:
        blockable = True

    student_informations = InternshipStudentInformation.find_all()
    for student_info in student_informations:
        if not student_info.check_coordonates :
            student_address = student_info.location + " " + student_info.postal_code + " " \
                            + student_info.city + " " + student_info.country
            student_address = student_address.replace('\n','')
            student_address_lat_long = geocode(student_address)
            student_info.latitude = student_address_lat_long[0]
            student_info.longitude = student_address_lat_long[1]
            student_info.check_coordonates = True
            student_info.save()

    organization_informations = OrganizationAddress.find_all()
    for organization_info in organization_informations:
        if not organization_info.check_coordonates :
            organization_address = organization_info.location + " " + organization_info.postal_code + " " \
                            + organization_info.city + " " + organization_info.country
            organization_address = organization_address.replace('\n','')
            organization_address_lat_long = geocode(organization_address)
            organization_info.latitude = organization_address_lat_long[0]
            organization_info.longitude = organization_address_lat_long[1]
            organization_info.check_coordonates = True
            organization_info.save()

    return render(request, "internships_home.html", {'section':   'internship',
                                                     'noma':      noma,
                                                     'blockable': blockable
                                                    })

def geocode(addr):
    lat_long = [None]*2
    # Transform the address for a good url and delete all accents
    addr = addr.replace(" ", "+")
    addr = addr.replace("'", "\'")
    addr = strip_accents(addr)
    # get the complete url
    url = "https://maps.googleapis.com/maps/api/geocode/xml?address=%s&key=AIzaSyCWeZdraxzqRTMxXxbXY3bncaD6Ijq_EvE" % addr

    # using urllib get the xml
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as response:
        data = response.read().decode('utf-8')

    # Parse the xml to have the latitude and longitude of the address
    xmldoc = minidom.parseString(data)
    lat = xmldoc.getElementsByTagName('location')
    for l in lat:
        c = l.getElementsByTagName('lat')[0].firstChild.data
        d = l.getElementsByTagName('lng')[0].firstChild.data
        lat_long[0] = c
        lat_long[1] = d
    # return the value
    return lat_long

def strip_accents(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s)
                   if unicodedata.category(c) != 'Mn')
