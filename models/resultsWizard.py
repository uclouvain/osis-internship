from openerp import models, fields, api

class ResultsWizard(models.TransientModel):
    _name = 'osis.wizard.result'

    exam_enrollment_id = fields.Many2one('osis.exam_enrollment', string='Exam enrollement')
    line_ids = fields.One2many('osis.wizard.result.line', 'result_id')


    @api.one
    def validate_results(self):
        print 'validate_results'
        res_model = self.env['osis.exam.result']
        res_model_ee = self.env['osis.exam_enrollment']
        for result in self.line_ids:
            print result.result
            res_ids = res_model.search([('exam_enrollment_id', '=', self.exam_enrollment_id.id), ('student_id', '=', result.student_id.id)])
            res_ee_ids = res_model_ee.search([('id', '=', self.exam_enrollment_id.id)])
            if res_ee_ids:
                res_ee_ids.write({'score': result.result})


        return True

class ResultsWizardLine(models.TransientModel):
    _name = 'osis.wizard.result.line'

    result_id = fields.Many2one('osis.wizard.result')
    student_id = fields.Many2one('osis.student', string='Student', required=True)
    result = fields.Float('Result')
