# -*- coding: utf-8 -*-

from openerp import models, fields, api

class Exam_enrollment(models.Model):
    _name = 'osis.exam_enrollment'
    _description = "Exam enrollment"

    exam_id = fields.Many2one('osis.exam', string='Exam')
    learning_unit_enrollment_id = fields.Many2one('osis.learning_unit_enrollment', string='Learning unit enrollment')
    score = fields.Float('Score')
