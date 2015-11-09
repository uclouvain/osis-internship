# -*- coding: utf-8 -*-

from openerp import models, fields, api

class Student(models.Model):
    _inherit = 'res.partner'

    registration_number = fields.Char('Registration number')
    # birth_place = fields.Char('Birth place')
    # birth_country = fields.Many2one('res.country')
    sexe = fields.Selection([('F','Female'),('M','Male'),('U','Unknown')], default= 'U')
    civil_status = fields.Selection([('MARRIED','Married'),('SINGLE','Single')])
    national_number = fields.Char('National registration number')# num social je pense que c'est num registre national
