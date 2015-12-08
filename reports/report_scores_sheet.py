-*- coding: utf-8 -*-

from openerp import models, fields, api
import openerp

class Report_scores_sheet(model.AbstractModel):
    _name = 'report.osis.report_scores_sheet'

    def get_academic_year(self):
        return 2222

    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('osis.report_scores_sheet')
        docargs = {
            'doc_ids': ids,
            'doc_model': report.model,
            'docs' : self.env[report.model].browse(ids),
            'get_academic_year' : self.get_academic_year,
        }
        return report_obj.render('osis.report_scores_sheet', docargs)
