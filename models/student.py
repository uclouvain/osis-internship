# -*- coding: utf-8 -*-

from openerp import models, fields, api


class Student(models.Model):
    _name = 'osis.student'
    # _inherits = {'osis.person' : 'person_id'}
    #
    registration_number = fields.Char('Registration number')
    sexe = fields.Selection([('F','Female'),('M','Male'),('U','Unknown')], default= 'U')
    civil_status = fields.Selection([('MARRIED','Married'),('SINGLE','Single'),('WIDOWED','Widowed'),('DIVORCED','Divorced'),('SEPARATED','Separated'),('CONCUBIN','Concubin')])
    national_number = fields.Char('National registration number')
    # person_id = fields.Many2one('osis.person')
