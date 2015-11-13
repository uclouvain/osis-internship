# -*- coding: utf-8 -*-

from openerp import models, fields, api

class Learning_unit_year(models.Model):
    _name = 'osis.learning_unit_year'
    _description = "Learning unit year"

    academic_year_id = fields.Many2one('osis.academic_year', string='Academic year')
    learning_unit_id = fields.Many2one('osis.learning_unit', string='Learning unit')
    attribution_entity_id = fields.Many2one('osis.structure', string='Attribution entity')
    specifications_responsible_id = fields.Many2one('osis.structure', string='Specifications responsible entity')

    credits = fields.Float("Credits", default=0)

    def name_get(self,cr,uid,ids,context=None):
        result={}
        for record in self.browse(cr,uid,ids,context=context):
            result[record.id]  = str(record.academic_year_id.year) + " - " + record.learning_unit_id.title
        return result.items()
