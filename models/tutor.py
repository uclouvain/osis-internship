# -*- coding: utf-8 -*-

from openerp import models, fields

class Tutor(models.Model):
    _name = 'osis.tutor'
    _inherits = {'osis.person' : 'person_id'}

    person_id = fields.Many2one('osis.person')
