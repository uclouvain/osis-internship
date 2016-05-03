##############################################################################
#
# OSIS stands for Open Student Information System. It's an application
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
from django.db import models
from django.utils import timezone
from django.contrib import admin
from base.models import offer_year

class OfferProposition(models.Model):
    title = models.CharField(max_length=200)#Nom du programme de cours
    offer_year = models.ForeignKey(offer_year.OfferYear)

    adviser_reader = models.BooleanField(default=False)
    # L enseignant peut il proposer un lecteur

    commission_validation = models.BooleanField(default=False)
    #Y a t il une commision de validation

    commission_readers = models.BooleanField(default=True)
    #la commission de lecture est elle gérée par le secrétariat ?
    #True pour Oui. Flase par l'étudiant (exemple :FOPA)

    evaluation_first_cicle = models.BooleanField(default=False)
    #la commission de lecture est-elle gérée par le secrétariat ? True pour Oui.
    #Flase pour géré par l'étudiant (exemple : requis FOPA)

    visibility_commission_readers = models.BooleanField(default=False)
    #Quelle visibilité pour la commission :
    #True : la visibilité est active dés la création de la commission
    #False : elle n'est visible qu'après l'encodage du titre définitif

    

    def __str__(self):
        return self.title
