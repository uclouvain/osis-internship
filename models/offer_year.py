# -*- coding: utf-8 -*-

from openerp import models, fields, api

class Offer_year(models.Model):
    _name = 'osis.offer_year'
    _description = "Offer year"

    offer_id = fields.Many2one('osis.offer', string='Offer')
    structure_id = fields.Many2one('osis.structure', string='Structure')
    academic_year_id = fields.Many2one('osis.academic_year', string='Academic Year')
    offer_enrollment_ids = fields.One2many('osis.offer_enrollment', 'offer_year_id')