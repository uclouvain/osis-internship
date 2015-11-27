# -*- coding: utf-8 -*-

from openerp import models, fields, api, tools, _
import openerp.pooler as pooler
import openerp
from openerp import SUPERUSER_ID

class Student_notes_display(models.Model):
    _name = 'osis.student_notes_display'
    _description = "Student notes display"
    _auto = False


    title_learning_unit = fields.Char('Title learning unit')
    # title_offer = fields.Char('Title offer')
    year = fields.Integer('Year')
    session_name = fields.Char('Session name')
    session_exam_id = fields.Char('Session exam id')
    student_name = fields.Char('Student name')
    score = fields.Char('Score')
    student_ref  = fields.Integer('Student ref')
    learning_unit_ref = fields.Integer('Learning unit id')
    learning_unit_enrollment_id = fields.Integer('Learning unit enrollment id')
    exam_enrollment_id = fields.Integer('Exam enrollment id')


    def init(self, cr):
        tools.sql.drop_view_if_exists(cr, 'osis_student_notes_display')
        cr.execute('''CREATE OR REPLACE VIEW osis_student_notes_display AS (
            select ay.year as year,
                   se.session_name as session_name,
                   ee.session_exam_id as session_exam_id,
                   p.name as student_name,
                   ee.score as score,
                   luy.learning_unit_id as learning_unit_ref,
                   lue.student_id as student_ref,
                   ee.id as id,
                   luy.title as title_learning_unit,
                   ee.learning_unit_enrollment_id as learning_unit_enrollment_id,
                   ee.id as exam_enrollment_id
            from osis_session_exam se join osis_exam_enrollment ee on ee.session_exam_id = se.id
                 join osis_learning_unit_year luy on se.learning_unit_year_id = luy.id
                 join osis_academic_year ay on luy.academic_year_id = ay.id
                 join osis_learning_unit_enrollment lue on lue.id = ee.learning_unit_enrollment_id
                 join osis_offer_enrollment oo on lue.offer_enrollment_id = oo.id
                 join osis_student s on s.id = oo.student_id
                 join osis_person p on s.person_id = p.id
                 join osis_learning_unit lu on luy.learning_unit_id = lu.id
                 where ee.encoding_status != 'SUBMITTED'
            )''')



    def submit_results(self, cr, uid, ids, context=None) :
        for rec in self.pool.get('osis.exam_enrollment').browse(cr, uid, ids, context=context):

            if rec.score is not None:
                ids_update = [rec.id]
                self.pool.get('osis.exam_enrollment').write(cr, uid, ids_update, {'encoding_status': 'SUBMITTED'})


    def wizard_encode_results(self, cr, uid, ids, context=None) :
        # ATTENTION : il faut simplifier cette requête (lecgture assez difficile)
        model_exam_enrollment = self.pool.get('osis.exam_enrollment')
        model_learning_unit_enrollment = self.pool.get('osis.learning_unit_enrollment')
        model_student = self.pool.get('osis.student')
        model_offer_enrollment = self.pool.get('osis.offer_enrollment')
        student_score_list=list()
        for exam_enrollment_id in ids:
            recs_ee = model_exam_enrollment.search(cr,uid,[('id','=',exam_enrollment_id)])
            for rec_ee in model_exam_enrollment.browse(cr, uid, recs_ee, context=context):

                session_exam_id = rec_ee.session_exam_id
                recs_lue = model_learning_unit_enrollment.search(cr,uid,[('id','=',rec_ee.learning_unit_enrollment_id.id)])
                for rec_lue in model_learning_unit_enrollment.browse(cr, uid, recs_lue, context=context):
                    recs_oe = model_offer_enrollment.search(cr,uid,[('id','=',rec_lue.offer_enrollment_id.id)])
                    for rec_oe in model_offer_enrollment.browse(cr, uid, recs_oe, context=context):
                        recs_s = model_student.search(cr,uid,[('id','=',rec_oe.student_id.id)])
                        for rec_s in model_student.browse(cr, uid, recs_s, context=context):
                            score_line = Line(rec_oe.student_id.id,rec_ee.score,exam_enrollment_id)
                            student_score_list.append(score_line)


        wiz_id = self.pool.get('osis.wizard.result').create(cr, uid,{
            'exam_enrollment_id': exam_enrollment_id,
            'line_ids':[(0,0,{'student_id': student.student_id,'result': student.score,'exam_enrollment_id':student.exam_enrollment_id}) for student in student_score_list],
        })


        idd = None
        for rec_w in self.pool.get('osis.wizard.result').browse(cr, uid, wiz_id, context=context):

            idd=rec_w.id

        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'osis.wizard.result',
            'res_id': idd,
            'target': 'new',
        }


class ExamResults(models.Model):
    _name = 'osis.exam.result'

    exam_enrollment_id = fields.Many2one('osis.exam_enrollment', string='Exam')
    student_id = fields.Many2one('osis.student', string='Student', required=True)
    result = fields.Float('Result')

class Line:

    def __init__(self, student_id ,score,exam_enrollment_id) :
        self.student_id = student_id
        self.score = score
        self.exam_enrollment_id = exam_enrollment_id
