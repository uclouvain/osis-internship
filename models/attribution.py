# -*- coding: utf-8 -*-

from openerp import models, fields, api

class Attribution(models.Model):
    _name = 'osis.attribution'
    _description = "Attribution"

    learning_unit_id = fields.Many2one('osis.learning_unit', string='Learning unit')
    tutor_id = fields.Many2one('osis.tutor', string='Tutor')
    start_year = fields.Integer('Starting year')
    end_year = fields.Integer('Ending year')
    duration = fields.Integer('Duration')
    function = fields.Selection([('UNKNOWN','Unknown'),('PROFESSOR','Professor'),('COORDINATOR','Coordinator')])
