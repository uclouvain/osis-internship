# -*- coding: utf-8 -*-

from openerp import models, fields

class Offer(models.Model):
    _name = "osis.offer"
    _description = "Offer"

    acronym  = fields.Char('Acronym')
    title = fields.Char('Title')
