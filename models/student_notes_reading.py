# -*- coding: utf-8 -*-

from openerp import models, fields, api, tools, _

class Student_notes_reading(models.Model):
    _name = 'osis.student.notes'
    _description = 'Student notes'
    _auto = False
    _order = 'title'

    title = fields.Char('Title', readonly=True)
    year = fields.Integer('Year', readonly=True)
    status = fields.Char('Status', readonly=True)
    session_name = fields.Char('Session name', readonly=True)
    exam_id = fields.Char('Exam id', readonly=True)
    learning_unit_year_id = fields.Integer('Learning Unit Year Id', readonly=True)


    def init(self, cr):
        print 'init'
        cr.execute('select distinct(exam_id) from osis_exam_enrollment')
        res_exam_ids = cr.fetchall()

        ids = []
        cpt=0
        for identifiant in res_exam_ids:
            ids.append(identifiant[0])


        tools.sql.drop_view_if_exists(cr, 'osis_student_notes')

        cr.execute('''CREATE OR REPLACE VIEW osis_student_notes AS (
            select e.status as status,
                   lu.title as title,
                   ay.year as year,
                   e.session_name as session_name,
                   e.id as exam_id,
                   e.learning_unit_year_id as learning_unit_year_id,
                   e.id as id
            from osis_exam e
                 join osis_learning_unit_year luy on e.learning_unit_year_id = luy.id
                 join osis_academic_year ay on luy.academic_year_id = ay.id
                 join osis_learning_unit lu on luy.learning_unit_id = lu.id
                 where e.id in %s

        )''',(tuple(ids),))


        cr.execute('select * from osis_student_notes')
        res = cr.fetchall()

        for r in res:
            print r



    @api.multi
    def display_students_notes(self):
       print 'methode display_students_notes'
       view_ref = self.env['ir.model.data'].get_object_reference('osis-louvain', 'student_notes_display_tree_view')
       view_id = view_ref[1] if view_ref else False
       print 'exam_id:', self.exam_id
       res = {
           'type': 'ir.actions.act_window',
           'name': _('Student notes'),
           'res_model': 'osis.student_notes_display',
           'view_type': 'tree',
           'view_mode': 'tree',
           'view_id': view_id,
           'target': 'current',
           'domain':[['exam_ref','=',self.exam_id]]

       }

       return res
