# -*- coding: utf-8 -*-

from openerp import models, fields, api, _, exceptions
import datetime
import xlsxwriter, StringIO, base64


class SessionExam(models.Model):
    _name = 'osis.session_exam'
    _description = "Session Exam"
    _sql_constraints = [('session_exam_unique','unique(learning_unit_year_id,number_session)','A session must be unique on number session/learning unit year')]

    encoding_status = fields.Selection([('COMPLETE','Complete'),('PARTIAL','Partial'),('MISSING','Missing')])
    number_session = fields.Selection([(1,'1'),(2,'2'),(3,'3')])
    comment = fields.Text('Comment')

    learning_unit_acronym = fields.Char(related="learning_unit_year_id.acronym")
    learning_unit_title = fields.Char(related="learning_unit_year_id.title")
    notes_count = fields.Integer(compute='_get_notes_count')
    registered_student_count = fields.Integer(compute='_get_registered_student_count')

    learning_unit_year_id = fields.Many2one('osis.learning_unit_year', string='Learning unit year')
    academic_year_id = fields.Many2one('osis.academic_year', related="learning_unit_year_id.academic_year_id")
    offer_filter_id = fields.Many2one('osis.offer', domain="[('id', 'in', offer_ids[0][2])]")

    exam_enrollment_ids = fields.One2many('osis.exam_enrollment','session_exam_id', string='Exam enrollment')
    notes_encoding_ids = fields.One2many('osis.notes_encoding','session_exam_id', string='Notes encoding')
    notes_encoding_filter_ids = fields.One2many('osis.notes_encoding','session_exam_id', compute='_get_encoding_filter',                                                                                         inverse='_set_encoding', string='Notes encoding')
    notes_encoding_compare_filter_ids = fields.One2many('osis.notes_encoding','session_exam_id', compute='_get_encoding_compare_filter', inverse='_set_encoding', string='Notes encoding')

    offer_ids = fields.Many2many('osis.offer', compute='_get_all_offer')
    tutor_ids = fields.Many2many('osis.tutor', compute='_get_all_tutor')


    @api.depends('offer_filter_id', 'notes_encoding_ids')
    def _get_encoding_compare_filter(self):
        # get_encoding_filter(self) #todo je sais pas si c'est nécessaire
        for rec in self.notes_encoding_filter_ids:
            if (rec.score_1 != rec.score_2) or rec.justification_1 != rec.justification_2:
                self.notes_encoding_compare_filter_ids |= rec


    @api.depends('offer_filter_id', 'notes_encoding_ids')
    def _get_encoding_filter(self):
        if not self.offer_filter_id:
            self.notes_encoding_filter_ids = self.notes_encoding_ids
        else:
            self.notes_encoding_filter_ids = self.notes_encoding_ids.filtered(lambda record: record.offer_id == self.offer_filter_id)

    def _set_encoding(self):
        pass #DO nothing since we do not want to change the list of ids we just want to write on osis.notes_encoding which is done automaticaly

    def _get_notes_count(self):
        self.notes_count = self.notes_encoding_ids.search_count([])

    def name_get(self,cr,uid,ids,context=None):
        result={}
        for record in self.browse(cr,uid,ids,context=context):
            name_build = ''
            if record.learning_unit_year_id:
                name_build += str(record.learning_unit_year_id.academic_year_id.year)
                if record.learning_unit_year_id.title:
                    name_build+= ' - '
                    name_build += record.learning_unit_year_id.title
            if record.number_session:
                if record.number_session:
                    name_build+= ' - '
                name_build += str(record.number_session)
            result[record.id]  = name_build
        return result.items()


    @api.multi
    def encode_session_notes(self):
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'osis.session_exam',
            'res_id': self.id,
            'view_id' : self.env.ref('osis_louvain.resultswizard_form_view').id,
            'target': 'new',
        }


    @api.multi
    def double_encode_session_notes(self):
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'osis.session_exam',
            'res_id': self.id,
            'view_id' : self.env.ref('osis_louvain.double_resultswizard_form_view').id,
            'target': 'new',
        }



    @api.multi
    def compare_session_notes(self):
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'osis.session_exam',
            'res_id': self.id,
            'view_id' : self.env.ref('osis_louvain.compare_resultswizard_form_view').id,
            'target': 'new',
        }

        # double_encoding_done = False
        # for rec_notes_encoding in self.notes_encoding_ids:
        #     if rec_notes_encoding.double_encoding_done:
        #         double_encoding_done=True
        #         break
        #self.offer_ids |= enrol.offer_enrollment_id.offer_year_id.offer_id
        # if double_encoding_done:
        #     notes_encoding_ids=[]
        #     for rec in self.notes_encoding_ids:
        #         if rec.score_1 != rec.score_2 or rec.justification_1  != rec.justification_2:
        #             notes_encoding_ids.append(rec)
        #
        #     if notes_encoding_ids:
        #         wiz_id = self.env['osis.notes_wizard'].create({
        #             'acronym': self.learning_unit_acronym,
        #
        #             'line_ids':[(0,0,{'notes_encoding_id': rec_notes_encoding.id,
        #                               'encoding_stage' : 3,
        #                               'student_name': rec_notes_encoding.student_name,
        #                               'score_1': rec_notes_encoding.score_1,
        #                               'justification_1':rec_notes_encoding.justification_1,
        #                               'score_2': rec_notes_encoding.score_2,
        #                               'justification_2':rec_notes_encoding.justification_2
        #                               }) for rec_notes_encoding in notes_encoding_ids],
        #         })
        #         print wiz_id.id
        #         return {
        #             'type': 'ir.actions.act_window',
        #             'view_type': 'form',
        #             'view_mode': 'form',
        #             'res_model': 'osis.notes_wizard',
        #             'res_id': wiz_id.id,
        #             'view_id' : self.env.ref('osis_louvain.compare_resultswizard_form_view').id,
        #             'target': 'new',
        #         }
        #     else:
        #         raise exceptions.ValidationError(_("All notes are identical"))
        # else:
        #     raise exceptions.ValidationError(_("Encode notes before double encoding"))

    @api.multi
    def open_session_notes(self):
        ''' Executed by "Notes" button in the encoding_notes_filter.xml '''
        self.ensure_one()
        for rec in self.exam_enrollment_ids:
            rec_date_remise = self.env['osis.academic_calendar'].search([('academic_year_id' ,'=', self.academic_year_id.id),('event','=',self.number_session)])
            print 'date remise : ', rec_date_remise[0].end_date

            date_remise = None
            if rec_date_remise[0]:
                date_remise=rec_date_remise[0].end_date
            rec_notes_encoding =  self.env['osis.notes_encoding'].search([('exam_enrollment_id' ,'=', rec.id)])
            if rec_notes_encoding:
                print 'kkk'
            else:
                if rec.encoding_status != 'SUBMITTED':

                    self.env['osis.notes_encoding'].create({'session_exam_id':self.id,
                                                            'exam_enrollment_id':rec.id,
                                                            'end_date':date_remise})

        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'osis.session_exam',
            'res_id': self.id,
            'target': 'inline',
            'view_id' : self.env.ref('osis_louvain.consulting_notes_session_form_primherit_view').id
        }

    @api.multi
    def encode_final_notes(self):
        print 'encode_final_notes'
        self.ensure_one()
        authorized = False
        for rec in self.notes_encoding_filter_ids:
            if rec.score_1 != rec.score_2 or rec.justification_1 != rec.justification_2:
                authorized = True

        if authorized:
            print 'authorized'
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'osis.session_exam',
                'res_id': self.id,
                'view_id' : self.env.ref('osis_louvain.encode_final_notes_form_view').id,
                'target': 'new',
            }
        else:
            print 'unauthorized'
            '''Ce bouton n'est disponible que quand les 2 colonnes notes ou les 2 colonnes motifs ne sont pas identiques'''
            raise exceptions.ValidationError(_("Unauthorized action,  notes/justifications must be non-identical for at leasts one student"))


    @api.multi
    def print_session_notes(self):
        datas = {
        'ids': [self.id]
        }
        return{
            'type' : 'ir.actions.report.xml',
            'report_name' : 'osis_louvain.report_session_exam_notes',
            'datas' : datas,
            }


    @api.depends('offer_filter_id')
    def _get_registered_student_count(self):
        self.registered_student_count = len(self.exam_enrollment_ids)


    @api.depends('learning_unit_year_id')
    def _get_all_offer(self):
        enrollement_ids = self.env['osis.learning_unit_enrollment'].search([('learning_unit_year_id', '=', self.learning_unit_year_id.id)])
        enrol_ids = []
        for enrol in enrollement_ids:
            enrol_ids.append(enrol.offer_enrollment_id.offer_year_id.offer_id.id)
            self.offer_ids |= enrol.offer_enrollment_id.offer_year_id.offer_id
            self.registered_student_count = enrol.offer_enrollment_id.student_id

    @api.depends('learning_unit_year_id')
    def _get_all_tutor(self):

        attribution_ids = self.env['osis.attribution'].search([('learning_unit_id', '=', self.learning_unit_year_id.learning_unit_id.id)])
        attrib_ids = []
        for a in attribution_ids:
            self.tutor_ids |= a.tutor_id

    def optimized_write_xlsx(self,info_to_write):
        output = StringIO.StringIO()
        workbook = xlsxwriter.Workbook(output, {'strings_to_urls': False})
        worksheet = workbook.add_worksheet()
        for i, row in enumerate(info_to_write):
            new_row = []
            for content in row:
                if type(content) in (str, unicode) and ('\n' in content or '\r' in content):
                    content = content.replace('\n',' ').replace('\r', '')
                new_row.append(content)
            worksheet.write_row('A' + str(i+1), new_row)
        workbook.close()
        return base64.encodestring(output.getvalue())

    @api.multi
    def xls_export_session_notes(self):

        # field_names=['score_1',
        # 'justification_1',
        # 'student_name' ,
        # 'student_registration_number',
        # 'offer']
        field_names=['academic_year',
                     'learning_unit',
                     'offer',
                     'student_registration_number',
                     'student_name',
                     'student_first_name',
                     'score_final',
                     'justification_final',
                     'end_date',
                     '.id']

        read = self.notes_encoding_ids.export_data(field_names)
        # body = [['Session Juin', '', ''],
        #         ['', 'Line2']]
        body = [['Academic year',
                 'Activity',
                 'Offer',
                 'Registration_number',
                 'Lastname',
                 'Firstname',
                 'Score_final',
                 'Justification_final',
                 'End_date',
                 'Id']]
        body += read['datas']

        import pprint; pprint.pprint(body)
        res = self.optimized_write_xlsx(body)
        rec_xls = self.env['osis.xls_print'].create({'content':res,'file_name':'session_notes.xlsx'})
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'osis.xls_print',
            'res_id': rec_xls.id,
            'target': 'new'

        }


    @api.multi
    def load_xls_session_notes(self):
        rec_xls = self.env['osis.xls_load'].create({})
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'osis.xls_load',
            'res_id': rec_xls.id,
            'target': 'new'
        }


    @api.one
    def validate_results(self):
        ''' Save the notes_encoding.  Executed : validate button '''
        return True


    @api.multi
    def submit_results(self):
        self.ensure_one()
        authorized = True
        for rec in self.notes_encoding_filter_ids:
            if rec.score_1 != rec.score_2 or rec.justification_1 != rec.justification_2:
                authorized = False

        if authorized:
            '''Ici on va sauver dans exam_enrollment et changer le status'''
            for rec in self.notes_encoding_filter_ids:
                rec_note.exam_enrollment_id.write({'score_draft': rec_note.score_1,
                                                   'justification_draft': rec_note.justification_1,
                                                   'score_reencoded': rec_note.score_2,
                                                   'justification_reencoded': rec_note.justification_2,
                                                   'score_final': rec_note.score_final,
                                                   'justification_final': rec_note.justification_final,
                                                   'encoding_status':'SUBMITTED'})
                #ici il faut supprimer l'enregistrement notes_encoding
                rec_note.unlink()
            return True
        else:
            '''Ce bouton n'est disponible que quand les 2 colonnes notes et les 2 colonnes motifs sont identiques'''
            raise exceptions.ValidationError(_("Unauthorized action,  notes/justifications must be identical for all student"))



    @api.multi
    def double_encoding(self):
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'osis.session_exam',
            'res_id': self.id,
            'view_id' : self.env.ref('osis_louvain.double_resultswizard_form_view').id,
            'target' : 'new'
        }
    @api.multi
    def save_comment(self):
        self.ensure_one()
        self.env['osis.session_exam'].browse(self.id).write({'comment' : self.comment})
        return True

    @api.multi
    def submit_final_notes(self):
        validate = True
        for record in self:
            for note in self.notes_encoding_compare_filter_ids:
                if note.score_final is None and note.justification_final is None:
                    validate = False
                    break

        if validate:
            return True
        else:
            raise exceptions.ValidationError(_("All notes must be encoded"))
