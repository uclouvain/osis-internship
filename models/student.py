# -*- coding: utf-8 -*-

from openerp import models, fields


class Student(models.Model):
    _name = 'osis.student'
    _rec_name = 'registration_number'

    registration_number = fields.Char('Registration number')

    person_id = fields.Many2one('osis.person', string="Person", required=True)
