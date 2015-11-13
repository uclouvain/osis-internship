# -*- coding: utf-8 -*-

from openerp import models, fields, api

class Learning_unit(models.Model):
    _name = 'osis.learning_unit'
    _description = 'Learning unit'
    _rec_name ='title'

    title = fields.Char('Title')
