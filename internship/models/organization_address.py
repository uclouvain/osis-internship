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
from django.contrib import admin
from django.db import models
import urllib.request
import unicodedata
from xml.dom import minidom
import logging
from internship.models.organization import Organization


class OrganizationAddressAdmin(admin.ModelAdmin):
    list_display = ('organization', 'label', 'location', 'postal_code', 'city', 'country', 'latitude', 'longitude')
    fieldsets = ((None, {'fields': ('organization', 'label', 'location', 'postal_code', 'city', 'country', 'latitude',
                                    'longitude')}),)
    raw_id_fields = ('organization',)


class OrganizationAddress(models.Model):
    organization = models.ForeignKey('Organization')
    label = models.CharField(max_length=20)
    location = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=20)
    city = models.CharField(max_length=255)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    country = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        has_organization = False
        try:
            has_organization = (self.organization is not None)
        except Exception:
            self.organization = Organization.objects.latest('id')

        self.label = "Addr"+self.organization.name[:14]
        super(OrganizationAddress, self).save(*args, **kwargs)


def geocode(addr):
    lat_long = [None]*2
    # Transform the address for a good url and delete all accents
    addr = addr.replace('\n','')
    addr = addr.replace(" ", "+")
    addr = addr.replace("'", "\'")
    addr = addr.replace("n°", "")
    addr = addr.replace("n °", "")
    addr = addr.replace("Œ", "Oe")
    addr = addr.encode('utf8','replace').decode('utf8')
    addr = OrganizationAddress.strip_accents(addr)
    # get the complete url
    url = ''.join(['https://maps.googleapis.com/maps/api/geocode/xml?address=', addr,
                   '&key=AIzaSyCWeZdraxzqRTMxXxbXY3bncaD6Ijq_EvE'])
    logging.info(url)

    # using urllib get the xml
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as response:
        data = response.read().decode('utf-8')

    # Parse the xml to have the latitude and longitude of the address
    xmldoc = minidom.parseString(data)
    status = xmldoc.getElementsByTagName('status')[0].firstChild.data
    if status == "OK":
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
        if data.latitude is None :
            #if it exist, compile the address with the location / postal / city / country
            address = data.location + " " + data.postal_code + " " \
                      + data.city + " " + data.country
            #Compute the geolocalisation
            address_lat_long = OrganizationAddress.geocode(address)
            #if the geolac is fing put the data, if not put fake data
            if address_lat_long[0]:
                data.latitude = address_lat_long[0]
                data.longitude = address_lat_long[1]
            else :
                address = data.location + " " + data.postal_code + " " \
                          + data.country
                #Compute the geolocalisation
                address_lat_long = OrganizationAddress.geocode(address)
                #if the geolac is fing put the data, if not put fake data
                if address_lat_long[0]:
                    data.latitude = address_lat_long[0]
                    data.longitude = address_lat_long[1]
                else :
                    data.latitude = 999
                    data.longitude = 999
            #save the data
            data.save()


def search(**kwargs):
    kwargs = {k: v for k, v in kwargs.items() if v}
    return OrganizationAddress.objects.filter(**kwargs).select_related("organization")


def find_by_id(organization_address_id):
    return OrganizationAddress.objects.get(pk=organization_address_id)
