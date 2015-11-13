# -*- coding: utf-8 -*-

from openerp import models, fields, api

class Exam(models.Model):
    _name = 'osis.exam'
    _description = "Exam"

    learning_unit_year_id = fields.Many2one('osis.learning_unit_year', string='Learning unit year')
    date_session = fields.Date('Session date')
    status = fields.Char('Status')
    closed = fields.Boolean(default = False)
