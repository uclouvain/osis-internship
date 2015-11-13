# -*- coding: utf-8 -*-

from openerp import models, fields, api, exceptions
import datetime

class Academic_year(models.Model):
    _name = "osis.academic_year"
    _description = "Academic year"
    _rec_name = "year"

    year = fields.Integer('Year', required = True)
    start_date = fields.Date('Start date')
    end_date = fields.Date('Start date')

    @api.constrains('start_date','end_date')
    def _check_dates(self):
        for record in self:
            if record.start_date:
                if record.end_date:
                    if fields.Datetime.from_string(record.start_date) > fields.Datetime.from_string(record.end_date):
                        raise exceptions.ValidationError("End date must be greater or equal than start year")
