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


###########################################################################
# TO RUN THE SCRIPT ALONE, UNCOMMENT 6 NEXT LINES
from sys import path
import os
import django
path.append('../')
os.environ["DJANGO_SETTINGS_MODULE"] = "backoffice.settings"
django.setup()
###########################################################################

from reference import models
from backoffice import queue


QUEUE_NAME = 'reference'


def get_all_datas(model_class, fields=None, order_by=None):
    """
    Récupère et renvoie tous les records en DB du modèle passé en paramètre.
    :param model_class: La classe du modèle Django (table)
    :param order_by: A string represent the name of a column in the model.
    :return: Liste des records sous forme de dictionnaire
    """
    print("Retrieving datas from " + str(model_class) + "...")
    queryset = model_class.objects
    if fields :
        queryset = queryset.values(*fields)
    else :
        queryset = queryset.values()
    if order_by :
        queryset = queryset.order_by(order_by)
    print("Done.")
    return list(queryset) # list() to force the evaluation of the queryset


def get_model_class_str(model_class):
    """
    Recherche la représentation en String (commune à Osis et Osis-portal) pour le modèle passé en paramètre.
    :return: un String qui représente le model_class passé en paramètre.
    """
    map_classes = {
        models.Country : 'reference.Country',
    }
    return map_classes[model_class]



def migrate(model_class, fields=None):
    """
    Récupère tous les records du modèle passé en paramètre et les envoie dans la queue.
    """
    records = get_all_datas(model_class, fields=fields, order_by='name')
    print("Sending records into the queue named '" + QUEUE_NAME + "'...")
    datas = {
        'model_class_str' : get_model_class_str(model_class),
        'records' : records,
    }
    queue.send_message(QUEUE_NAME, datas)
    print("Done.")


def execute():
    """
    Lance la migration de Osis.Country vers Osis-portal.Country.
    """
    # migrate(models.Continent)
    # migrate(models.Currency)
    migrate(models.Country, fields=['id', 'iso_code', 'name', 'nationality', 'european_union', 'dialing_code', 'cref_code'])


execute()
