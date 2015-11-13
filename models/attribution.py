# -*- coding: utf-8 -*-

from openerp import models, fields, api, tools, exceptions
import datetime


class Attribution(models.Model):
    _name = 'osis.attribution'
    _description = "Attribution"

    learning_unit_id = fields.Many2one('osis.learning_unit', string='Learning unit')
    tutor_id = fields.Many2one('osis.tutor', string='Tutor')
    start_date = fields.Date('Start date', required = True)
    end_date = fields.Date('End date')
    function = fields.Selection([('UNKNOWN','Unknown'),('PROFESSOR','Professor'),('COORDINATOR','Coordinator')])

    @api.constrains('start_date','end_date')
    def _check_dates(self):
        for record in self:
            if record.start_date:
                if record.end_date:
                    if fields.Datetime.from_string(record.start_date) > fields.Datetime.from_string(record.end_date):
                        raise exceptions.ValidationError("End date must be greater or equal than start year")
