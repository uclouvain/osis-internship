# -*- coding: utf-8 -*-
##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2016 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    A copy of this license - GNU Affero General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################

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
