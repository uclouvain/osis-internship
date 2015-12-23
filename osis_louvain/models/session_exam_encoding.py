# -*- coding: utf-8 -*-
from openerp import models, fields, api, exceptions, _
from datetime import datetime

class SessionExamEncoding(models.TransientModel):
    _name = 'osis.session_exam_encoding'

    def _get_default_academic_year(self):
        ''' Compute the default academic year '''

        today = datetime.now()
        today_str = fields.Datetime.to_string(today)
        recs = self.env['osis.academic_year'].search([('start_date', '<=', today_str),
                                                     ('end_date', '>=', today_str)])
        if recs:
            for rec in recs:
                return rec
        return None;


    def _get_default_session_number(self):
        ''' Compute the default session number '''
        #todo session_number par defaut pas très bien calculé à améliorer
        today = datetime.now()
        month_num = today.strftime("%m")
        print month_num
        if month_num > 1 and month_num<=6:
            return 6
        if month_num > 6 and month_num<=9:
            return 9
        else:
            return 1


    tutor = fields.Many2one('osis.tutor', string='Tutor',)
    academic_year = fields.Many2one('osis.academic_year', string='Academic year', default=_get_default_academic_year)
    session_month_selection = fields.Selection([(1,'1'),(2,'2'),(3,'3')], default = _get_default_session_number)
    session_exam_ids = fields.Many2many('osis.session_exam', 'rel_sessions', 'session_exam_encoding_id','session_exam_id',string='Sessions', readonly=True)


    @api.one
    def _set_session_list(self):
        if self.tutor and self.academic_year and self.session_month_selection:
            self.session_exam_ids = self.env['osis.session_exam'].search([
                                                         ('learning_unit_year_id.learning_unit_id.attribution_ids.tutor_id', '=', self.tutor.id),
                                                         ('learning_unit_year_id.academic_year_id', '=', self.academic_year.id),
                                                         ('number_session', 'ilike', self.session_month_selection)])
        else:
            self.session_exam_ids=None


    @api.model
    def tutor_encoding_notes(self):
        rec= self.env['osis.tutor'].search([('person_id.partner_id', '=', self.env.user.partner_id.id)])
        rec_session_exam_encoding = self.env['osis.session_exam_encoding'].create({'tutor':rec.id})
        rec_session_exam_encoding._set_session_list()

        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'osis.session_exam_encoding',
            'res_id': rec_session_exam_encoding.id,
            'target': 'inline'
        }
