# -*- coding: utf-8 -*-

from openerp import models, fields, api

class Structure(models.Model):
    _name = "osis.structure"
    _description = "Structure"
    _rec_name='title'

    title = fields.Char('Title')
