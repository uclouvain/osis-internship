# -*- coding: utf-8 -*-

from openerp import models, fields


class Person(models.Model):
    _name = 'osis.person'
    _inherits = {'res.partner' : 'partner_id'}

    identification_number = fields.Char('Identification number')
    partner_id = fields.Many2one('res.partner')
