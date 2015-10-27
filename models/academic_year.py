# -*- coding: utf-8 -*-

from openerp import models, fields, api

class Academic_year(models.Model):
    _name = "osis.academic_year"
    _description = "Academic year"

    offer_year_ids = fields.One2many('osis.offer_year', 'academic_year_id')
    learning_unit_year_ids = fields.One2many('osis.learning_unit_year', 'academic_year_id')
