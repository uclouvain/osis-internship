# -*- coding: utf-8 -*-

from openerp import models, fields, api

class Learning_unit(models.Model):
    _name = 'osis.learning_unit'
    _description = "Learning unit"

    title = fields.Char('Title')
    attribution_id = fields.One2many('osis.attribution', 'learning_unit_id', string='Attribution')
    learning_unit_year_id = fields.One2many('osis.learning_unit_year', 'learning_unit_id' ,string='Learning Unit Year')
