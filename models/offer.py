# -*- coding: utf-8 -*-

from openerp import models, fields, api

class Offer(models.Model):
    _name = "osis.offer"
    _description = "Offer"
    _rec_name = "acronym"

    acronym  = fields.Char('Acronym', required = True)
    title = fields.Text('Title')

    @api.onchange('acronym')
    def _upper_acronym(self):
        if self.acronym:
            self.acronym = self.acronym.upper()
