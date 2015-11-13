# -*- coding: utf-8 -*-

from openerp import models, fields

class Tutor(models.Model):
    _name = 'osis.tutor'
    # _rec_name = 'person_id' ca écrit false
    _description = 'person_id' #ça écrit osis.tutor.1

    person_id = fields.Many2one('osis.person', string="Person", required=True)


    #Pour voir le nom du tutor dans la liste des attributions notamment
    def name_get(self,cr,uid,ids,context=None):
        result={}
        for record in self.browse(cr,uid,ids,context=context):
            result[record.id]  = record.person_id.name
        return result.items()
