from openerp import models, fields, api, exceptions, _

class ResultsWizard(models.TransientModel):
    _name = 'osis.wizard.result'

    exam_enrollment_id = fields.Many2one('osis.exam_enrollment', string='Exam enrollement')
    line_ids = fields.One2many('osis.wizard.result.line', 'result_id')

    @api.one
    def validate_results(self):
        res_model_ee = self.env['osis.exam_enrollment']
        for result in self.line_ids:
            res_ee_ids = res_model_ee.search([('id', '=', result.exam_enrollment_id)])
            if res_ee_ids:
                res_ee_ids.write({'score': result.result})
        return True


class ResultsWizardLine(models.TransientModel):
    _name = 'osis.wizard.result.line'

    result_id = fields.Many2one('osis.wizard.result')
    exam_enrollment_id = fields.Integer('Exam enrollment')
    student_id = fields.Many2one('osis.student', string='Student', required=True)
    result = fields.Float('Result')

    @api.constrains('result')
    def _check_dates(self):
        for record in self:
            if record.result:
                if record.result < 0:
                    raise exceptions.ValidationError(_("The score must be greater or equal to 0"))
                if record.result > 20:
                    raise exceptions.ValidationError(_("The score must be less than or equal to 20"))
