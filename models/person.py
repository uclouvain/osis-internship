# -*- coding: utf-8 -*-

from openerp import models, fields, api


class Person(models.Model):
    _name = 'osis.person'
    _inherit = 'res.partner'

    last_name = fields.Char('Last name')
    first_name = fields.Char('First name')
    middle_name = fields.Char('Middle name')
    global_id = fields.Char('Global ID')
    gender = fields.Selection([('F','Female'),('M','Male'),('U','Unknown')], default= 'U')
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

    @api.multi
    def write(self, vals):
        name = str(vals.get('last_name')) + ' ' +str(vals.get('first_name'))
        nom=''
        if vals.get('last_name') is None:
            nom = u"%s" % self.last_name
        else:

            nom = u"%s" % vals.get('last_name')
        if vals.get('last_name') is None:
            prenom = u"%s" % self.first_name
        else:
            prenom = u"%s" % vals.get('first_name')
        if vals.get('middle_name') is None:
            prenoms = u"%s" % self.middle_name
        else:
            prenoms = u"%s" % vals.get('middle_name')
        name = u"%s %s %s" % (nom,prenom,prenoms)
        vals['name']=name
        # self['name'] = self['last_name'] + self['first_name']
        return super(Person, self).write(vals)
