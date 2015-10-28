# -*- coding: utf-8 -*-

from openerp import models, fields, api

class Structure(models.Model):
    _name = "osis.structure"
    _description = "Structure"

    offer_year_ids = fields.One2many('osis.offer_year', 'structure_id')
    learning_unit_year_ids = fields.One2many('osis.learning_unit_year', 'structure_id')
