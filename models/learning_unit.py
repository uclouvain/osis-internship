# -*- coding: utf-8 -*-

from openerp import models, fields, api

class Learning_unit(models.Model):
    _name = 'osis.learning_unit'
    _description = "Learning unit"

    number = fields.Integer('Number')
    start_year = fields.Integer('Starting year')
    endyear = fields.Integer('Ending year')
