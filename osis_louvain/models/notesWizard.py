# -*- coding: utf-8 -*-
from openerp import models, fields, api, exceptions, _

class NotesWizard(models.TransientModel):
    _name = 'osis.notes_wizard'

    acronym = fields.Char('Learning unit')
    line_ids = fields.One2many('osis.wizard.note.line', 'result_id')

class NotesWizardLine(models.TransientModel):
    _name = 'osis.wizard.note.line'

    result_id = fields.Many2one('osis.notes_wizard')
    encoding_stage = fields.Integer()
    notes_encoding_id = fields.Many2one('osis.notes_encoding')
    student_name = fields.Char('Student')
    score_1 = fields.Float('Score 1')
    justification_1 = fields.Selection([('ILL',_('Ill')),('ABSENT',_('Absent')),('JUSTIFIED_ABSENCE',_('Justified absence')),('CHEATING',_('Cheating')),('SCORE_MISSING',_('Score missing'))])
    score_2 = fields.Float('Score 2')
    justification_2 = fields.Selection([('ILL',_('Ill')),('ABSENT',_('Absent')),('JUSTIFIED_ABSENCE',_('Justified absence')),('CHEATING',_('Cheating')),('SCORE_MISSING',_('Score missing'))])
    score_final = fields.Float('Score final')
    justification_final = fields.Selection([('ILL',_('Ill')),('ABSENT',_('Absent')),('JUSTIFIED_ABSENCE',_('Justified absence')),('CHEATING',_('Cheating')),('SCORE_MISSING',_('Score missing'))])
