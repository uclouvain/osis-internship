# -*- coding: utf-8 -*-

from openerp import models, fields, api

class Learning_unit_year(models.Model):
    _name = 'osis.learning_unit_year'
    _description = "Learning unit year"
    _order = "academic_year_id"
    _sql_constraints = [('learning_unit_year_unique','unique(learning_unit_id,academic_year_id)','A learning unit year must be unique on academic year/learning unit year')]


    title = fields.Char('Title', required = True)
    acronym = fields.Char('Acronym', required = True)

    academic_year_id = fields.Many2one('osis.academic_year', string='Academic year')
    learning_unit_id = fields.Many2one('osis.learning_unit', string='Learning unit')

    credits = fields.Float("Credits", default=0)
    learning_unit_enrollment_ids = fields.One2many('osis.learning_unit_enrollment', 'learning_unit_year_id', string='Learning unit enrollment')
    session_exam_ids = fields.One2many('osis.session_exam', 'learning_unit_year_id', string='Session exam')



    def name_get(self,cr,uid,ids,context=None):
        result={}
        for record in self.browse(cr,uid,ids,context=context):
            title = u"%s" % record.title
            acronym = u"%s" % record.acronym
            result[record.id] = u"%s - %s" % (acronym,title)
        return result.items()
