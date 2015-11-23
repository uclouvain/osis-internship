from openerp import models, fields, api

class ResultsWizard(models.TransientModel):
    _name = 'osis.wizard.result'

    exam_enrollment_id = fields.Many2one('osis.exam_enrollment', string='Exam enrollement')
    line_ids = fields.One2many('osis.wizard.result.line', 'result_id')


    @api.one
    def validate_results(self):
        res_model = self.env['osis.exam.result']
        for result in self.line_ids:
            res_ids = res_model.search([('exam_enrollment_id', '=', self.exam_enrollment_id.id), ('student_id', '=', result.student_id.id)])
            if res_ids:
                res_ids.write({'result': result.result})
            else:
                res_model.create({'exam_enrollment_id': self.exam_enrollment_id.id, 'student_id': result.student_id.id,'result': result.result})

        return True

class ResultsWizardLine(models.TransientModel):
    _name = 'osis.wizard.result.line'

    result_id = fields.Many2one('osis.wizard.result')
    student_id = fields.Many2one('osis.student', string='Student', required=True)
    result = fields.Float('Result')
