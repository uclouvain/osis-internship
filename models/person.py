# -*- coding: utf-8 -*-

from openerp import models, fields


class Person(models.Model):
    _name = 'osis.person'
    _inherits = {'res.partner' : 'partner_id'}

    identification_number = fields.Char('Identification number')
    partner_id = fields.Many2one('res.partner')

    # student = fields.Boolean("Student", compute = "_get_is_student")
    #
    # @api.one
    # def _get_is_student(self):
    #     nbr = self.env['osis.student'].sudo().search_count([('person_id','=',self.id)])
    #     if nbr > 0:
    #         self.student = True
    #     else:
    #         self.student = False
