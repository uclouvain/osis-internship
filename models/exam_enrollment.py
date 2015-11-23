# -*- coding: utf-8 -*-
##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2016 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    A copy of this license - GNU Affero General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################

from openerp import models, fields, api, _

class Exam_enrollment(models.Model):
    _name = 'osis.exam_enrollment'
    _description = "Exam enrollment"

    exam_id = fields.Many2one('osis.exam', string='Exam')
    learning_unit_enrollment_id = fields.Many2one('osis.learning_unit_enrollment', string='Learning unit enrollment')
    score = fields.Float('Score')
    justification = fields.Selection([('ILL',_('Ill')),('ABSENT',_('Absent')),('JUSTIFIED_ABSENCE',_('Justified absence')),('CHEATING',_('Cheating')),('SCORE_MISSING',_('Score missing'))])


#     @api.multitr
#     def wizard_encode_results(self):
#
#         lue_id = self.learning_unit_enrollment_id.id
#         lue = self.env['osis.learning_unit_enrollment'].search([('id','=',lue_id)])
#         students = self.env['osis.student'].search([('learning_unit_enrollment_id','=',lue.id)])
#
#         wiz_id = self.env['osis.wizard.result'].create({
#             'exam_enrollment_id': self.id,
#             'line_ids':[(0,0,{'student_id': student.id}) for student in students],
#         })
#         return {
#             'type': 'ir.actions.act_window',
#             'view_type': 'form',
#             'view_mode': 'form',
#             'res_model': 'osis.wizard.result',
#             'res_id': wiz_id.id,
#             'target': 'new',
#         }
#
# class ExamResults(models.Model):
#     _name = 'epc.exam.result'
#
#     exam_enrollment_id = fields.Many2one('epc.exam_enrollment', string='Exam')
#     student_id = fields.Many2one('osis.student', string='Student', required=True)
#     result = fields.Float('Result')
