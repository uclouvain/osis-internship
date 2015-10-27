# -*- coding: utf-8 -*-

from openerp import models, fields, api

class Student(models.Model):
    _name = 'osis.student'
    _description = "Student"

    offer_enrollment_ids = fields.One2many('osis.offer_enrollment', 'student_id')
    learning_unit_enrollment_ids = fields.One2many('osis.learning_unit_enrollment', 'student_id')
