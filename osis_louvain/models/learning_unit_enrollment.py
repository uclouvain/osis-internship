# -*- coding: utf-8 -*-

from openerp import models, fields, api

class Learning_unit_enrollment(models.Model):
    _name = 'osis.learning_unit_enrollment'
    _description = "Learning unit enrollment"
    _sql_constraints = [('learning_unit_enrollment_unique','unique(offer_enrollment_id,learning_unit_year_id)','A learning unit enrollment must be unique on offer enrollment/learning_unit_year_id')]


    learning_unit_year_id = fields.Many2one('osis.learning_unit_year', string='Learning unit year')
    date_enrollment = fields.Date('Enrollment date')
    exam_enrollment_ids = fields.One2many('osis.exam_enrollment', 'learning_unit_enrollment_id', string='Learning unit enrollment')
    offer_enrollment_id = fields.Many2one('osis.offer_enrollment', string='Offer enrollment')


    def name_get(self,cr,uid,ids,context=None):
        result={}
        for record in self.browse(cr,uid,ids,context=context):
            year = u"%s" % record.learning_unit_year_id.academic_year_id.year
            title = u"%s" % record.learning_unit_year_id.title
            offer_acronym = u"%s" % record.offer_enrollment_id.offer_year_id.offer_id.acronym
            student = u"%s" % record.offer_enrollment_id.student_id.person_id.name
            result[record.id] = u"%s - %s - %s - %s" % (year,title,offer_acronym,student)
        return result.items()
