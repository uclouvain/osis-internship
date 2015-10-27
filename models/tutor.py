# -*- coding: utf-8 -*-

from openerp import models, fields, api

class Tutor(models.Model):
    _name = 'osis.tutor'
    _description = "Tutor"

    attribution_ids = fields.One2many('osis.attribution', 'tutor_id')
