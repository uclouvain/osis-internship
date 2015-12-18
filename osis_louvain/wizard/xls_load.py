from openerp import models, fields, api, exceptions, _
from datetime import datetime
import xlrd, base64

class XlsLoad(models.TransientModel):
    _name = 'osis.xls_load'

    content = fields.Binary()
    file_name = fields.Char()

    @api.one
    def load_xls_data(self):
        # Open the workbook
        xl_workbook = xlrd.open_workbook(file_contents=base64.decodestring(self.content))


        # Or grab the first sheet by index
        #  (sheets are zero-indexed)
        #
        xl_sheet = xl_workbook.sheet_by_index(0)


        # Print all values, iterating through rows and columns
        #
        header = ['score_1','registration_number','encoding_notes_id']
        values=[]
        num_cols = xl_sheet.ncols   # Number of columns
        for row_idx in range(1, xl_sheet.nrows):    # Iterate through rows
            values_col=[]
            for col_idx in range(0, num_cols):  # Iterate through columns
                cell_obj = xl_sheet.cell(row_idx, col_idx)
                values_col.append(cell_obj.value)
            values.append(dict(zip(header,values_col)))
        for encoding_data in values:
            encoding_id = int(encoding_data.pop('encoding_notes_id'))
            self.env['osis.notes_encoding'].browse(encoding_id).write({'score_1' : encoding_data['score_1']})
