# -*- coding: utf-8 -*-

from openerp import models, fields

class Tutor(models.Model):
    _name = 'osis.tutor'
    _description = 'Tutor'

    person_id = fields.Many2one('osis.person', string="Person", required=True)
