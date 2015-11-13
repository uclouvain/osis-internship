# -*- coding: utf-8 -*-

from openerp import models, fields, api


class Person(models.Model):
    _name = 'osis.person'
    _inherit = 'res.partner'

    global_id = fields.Char('Global ID')
    sexe = fields.Selection([('F','Female'),('M','Male'),('U','Unknown')], default= 'U')
    civil_status = fields.Selection([('MARRIED','Married'),('SINGLE','Single'),('WIDOWED','Widowed'),('DIVORCED','Divorced'),('SEPARATED','Separated'),('CONCUBIN','Concubin')])
    national_number = fields.Char('National number')

    # tutor_id = fields.Many2one('osis.tutor', string="Tutor")

    # student = fields.Boolean("Student", compute = "_get_is_student")
    #
    # @api.one
    # def _get_is_student(self):
    #     nbr = self.env['osis.student'].sudo().search_count([('person_id','=',self.id)])
    #     if nbr > 0:
    #         self.student = True
    #     else:
    #         self.student = False
