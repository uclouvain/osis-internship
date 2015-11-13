# -*- coding: utf-8 -*-

from openerp import models, fields, api

class Offer_enrollment(models.Model):
    _name = 'osis.offer_enrollment'
    _description = "Offer enrollment"

    offer_year_id = fields.Many2one('osis.offer_year', string='Offer year')
    student_id = fields.Many2one('osis.student', string='Student')

    date_enrollment = fields.Date('Enrollment date')
