# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
import datetime


class Exam(models.Model):
    _name = 'osis.exam'
    _description = "Exam"
    _rec_name = "session_name"

    learning_unit_year_id = fields.Many2one('osis.learning_unit_year', string='Learning unit year')
    date_session = fields.Date('Session date')
    status = fields.Selection([('COMPLETE',_('Complete')),('PARTIAL',_('Partial')),('MISSING',_('Missing'))])
    closed = fields.Boolean(default = False)
    session_name = fields.Char('Session Name',compute='_get_session_name', store=True)

    @api.depends('date_session')
    def _get_session_name(self):
        for r in self:
            r.session_name=''
            if r.date_session:
                session_date = fields.Datetime.from_string(r.date_session)
                r.session_name=session_date.strftime("%B")
