# -*- coding: utf-8 -*-
from openerp import models, fields, api, tools, _

class Student_notes_reading(models.Model):
    _name = 'osis.student_notes'
    _description = 'Student notes'
    _auto = False
    _order = 'acronym'

    acronym = fields.Char('Acronym', readonly=True)
    title = fields.Char('Title', readonly=True)
    year = fields.Integer('Year', readonly=True)
    status = fields.Char('Status', readonly=True)
    session_name = fields.Char('Session name', readonly=True)
    session_exam_id = fields.Char('Exam id', readonly=True)
    learning_unit_year_id = fields.Integer('Learning Unit Year Id', readonly=True)
    tutor_name = fields.Char('Tutor name', readonly=True)

    def init(self, cr):
        tools.sql.drop_view_if_exists(cr, 'osis_student_notes')

        cr.execute('''CREATE OR REPLACE VIEW osis_student_notes AS (
            select se.closed as status,
                   luy.title as title,
                   ay.year as year,
                   se.session_name as session_name,
                   se.id as session_exam_id,
                   se.learning_unit_year_id as learning_unit_year_id,
                   se.id as id,
                   luy.acronym as acronym
            from osis_session_exam se
                 join osis_learning_unit_year luy on se.learning_unit_year_id = luy.id
                 join osis_academic_year ay on luy.academic_year_id = ay.id
                 join osis_learning_unit lu on luy.learning_unit_id = lu.id
                 left join osis_attribution at  on at.learning_unit_id = lu.id

        )''',)
        # ids=[]
        # ids.append(421)
        # ids.append(422)
        #
        #
        # self.pool.get('ir.actions.actions').create(ids)


    @api.multi
    def display_students_notes(self):
       print 'methode display_students_notes'
       view_ref = self.env['ir.model.data'].get_object_reference('osis-louvain', 'student_notes_display_tree_view')
       view_id = view_ref[1] if view_ref else False

       res = {
           'type': 'ir.actions.act_window',
           'name': _('Student notes'),
           'res_model': 'osis.student_notes_display',
           'view_type': 'tree',
           'view_mode': 'tree',
           'view_id': view_id,
           'target': 'current',
           'domain':[['exam_ref','=',self.session_exam_id]]
       }

       return res
