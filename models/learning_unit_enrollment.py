# -*- coding: utf-8 -*-

from openerp import models, fields, api

class Learning_unit_enrollment(models.Model):
    _name = 'osis.learning_unit_enrollment'
    _description = "Learning unit enrollment"

    student_id = fields.Many2one('osis.student', string='Student')
    learning_unit_year_id = fields.Many2one('osis.learning_unit_year', string='Learning unit year')
    exam_enrollment_ids = fields.One2many('osis.exam_enrollment', 'learning_unit_enrollment_id')

