# -*- coding: utf-8 -*-

from openerp import models, fields, api

class Offer(models.Model):
    _name = "osis.offer"
    _description = "Offer"

    offer_year_ids = fields.One2many('osis.offer_year', 'offer_id')