# -*- coding: utf-8 -*-

from openerp import models, fields, api

class Offer_year(models.Model):
    _name = 'osis.offer_year'
    _description = "Offer year"
    _sql_constraints = [('offer_year','unique(academic_year_id,offer_id)','An offer year must be unique on academic year/offer')]

    offer_id = fields.Many2one('osis.offer', string='Offer')
    structure_id = fields.Many2one('osis.structure', string='Structure')
    academic_year_id = fields.Many2one('osis.academic_year', string='Academic Year')
    offer_enrollment_ids = fields.One2many('osis.offer_enrollment', 'offer_year_id', string='Offer enrollment')

    def name_get(self,cr,uid,ids,context=None):
        result={}
        for record in self.browse(cr,uid,ids,context=context):
            acronym = u"%s" % record.offer_id.acronym
            year = u"%s" % record.academic_year_id.year
            result[record.id] = u"%s - %s" % (acronym,year)
        return result.items()
