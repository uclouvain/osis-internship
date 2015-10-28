# -*- coding: utf-8 -*-

from openerp import models, fields, api

class Learning_unit_year(models.Model):
    _name = 'osis.learning_unit_year'
    _description = "Learning unit year"

    academic_year_id = fields.Many2one('osis.academic_year', string='Academic year')
    structure_id = fields.Many2one('osis.structure', string='Structure')
    learning_unit_id = fields.Many2one('osis.learning_unit', string='Learning unit')
    exam_ids = fields.One2many('osis.exam', 'learning_unit_year_id')
