# -*- coding: utf-8 -*-

from openerp import models, fields, api

class Offer_year(models.Model):
    _name = 'osis.offer_year'
    _description = "Offer year"

    offer_id = fields.Many2one('osis.offer', string='Offer')
    structure_id = fields.Many2one('osis.structure', string='Structure')
    academic_year_id = fields.Many2one('osis.academic_year', string='Academic Year')

    def name_get(self,cr,uid,ids,context=None):
        result={}
        for record in self.browse(cr,uid,ids,context=context):
            result[record.id]  = record.offer_id.acronym + "( " + str(record.academic_year_id.year) + ")"
        return result.items()
