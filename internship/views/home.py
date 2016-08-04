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

    #Find all informations about students and organisation and fin the latitude and longitude of the address
    student_informations = InternshipStudentInformation.search()
    organization_informations = OrganizationAddress.search()
    find_latitude_longitude(student_informations)
    find_latitude_longitude(organization_informations)

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

def find_latitude_longitude(infos):
    #for each data in the infos, check if the lat exist
    for data in infos:
        if data.latitude == None :
            #if it exist, compile the address with the location / postal / city / country
            address = data.location + " " + data.postal_code + " " \
                            + data.city + " " + data.country
            address = address.replace('\n','')
            #Compute the geolocalisation
            address_lat_long = geocode(address)
            #if the geolac is fing put the data, if not put fake data
            if address_lat_long[0] != None:
                data.latitude = address_lat_long[0]
                data.longitude = address_lat_long[1]
            else :
                data.latitude = 999
                data.longitude = 999
        #save the data
        data.save()
