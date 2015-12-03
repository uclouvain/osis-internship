# -*- coding: utf-8 -*-

from openerp import models, fields, api, tools, _
import openerp.pooler as pooler
import openerp
from openerp import SUPERUSER_ID

class Scores_sheet_report(models.Model):
    _name = 'osis.scores_sheet_report'
    _description = "Scores sheet report"
    _auto = False

    academic_year = fields.Char('Academic year')
    session_name = fields.Char('Session')
    learning_unit_title = fields.Char('Learning unit title')
    student_name = fields.Char('Student')

    def init(self, cr):
        tools.sql.drop_view_if_exists(cr, 'osis_scores_sheet_report')
        cr.execute('''CREATE OR REPLACE VIEW osis_scores_sheet_report AS (
            select ay.complete_year as academic_year,
                se.session_name as session_name,
                luy.title as learning_unit_title,
                p.name as student_name
            from osis_session_exam se
                join osis_learning_unit_year luy on luy.id= se.learning_unit_year_id
                join osis_academic_year ay on ay.id = luy.academic_year_id
                join osis_exam_enrollment ee on ee.session_exam_id = se.id
                join osis_learning_unit_enrollment lue on lue.id = ee.learning_unit_enrollment_id
                join osis_offer_enrollment oe on oe.id = lue.offer_enrollment_id
                join osis_student s on s.id = oe.student_id
                join osis_person p on s.person_id = p.id
            )''')
