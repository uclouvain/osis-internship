# -*- coding: utf-8 -*-

from openerp import models, fields, api, tools, exceptions, _
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
                        raise exceptions.ValidationError(_("End date must be greater or equal than start year"))

    def name_get(self,cr,uid,ids,context=None):
        result={}
        for record in self.browse(cr,uid,ids,context=context):
            result[record.id]  = str(record.learning_unit_id.title) + " - " + record.tutor_id.person_id.name
        return result.items()
