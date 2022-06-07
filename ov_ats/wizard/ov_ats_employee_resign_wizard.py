# -*- coding: utf-8 -*-

from odoo import models, fields, api

class EmployeeResignTrackWizard(models.TransientModel):
    _name = 'employee.resign'
    _description = 'Wizard'

    def _default_employee(self):
        return self.env['hr.employee'].browse(self._context.get('active_ids'))

    def _default_ats(self):
        val = self.env['hr.employee'].browse(self._context.get('active_ids'))
        return val.related_applicant

    def _default_joined_date(self):
        val = self.env['hr.employee'].browse(self._context.get('active_ids'))
        return val.commencement_date

    employee_ids = fields.Many2one('hr.employee', string="Employee", required=True, default=_default_employee)
    applicant_ids = fields.Many2one('hr.applicant', string="Related ATS Record", default=_default_ats)
    track_employee = fields.Boolean("Track this employee record?")
    delete_ats = fields.Boolean("Delete this employee's application (ATS) record?")
    joined_date = fields.Date("Joined Date", default=_default_joined_date)
    resignation_date = fields.Date("Resignation Date")
    resignation_reason = fields.Text("Reason")

    @api.multi
    def unlink_record(self):

        emp_track = self.track_employee
        ats_delete = self.delete_ats
        emp_ids = self.employee_ids
        app_ids = self.applicant_ids
        source = self.env['wss.campaign'].search([])
        resignation_details = self.env['employee.resignation.details'].search([])

        if (emp_track == False):
            emp_ids.write({'employee': False,'resigned': True,'terminated': False})
        if (emp_track == True):
            emp_ids.write({'employee': False,'resigned': True,'terminated': False})
            # pass
        if (ats_delete == True):
            app_ids.unlink()

        for s in source:
            if(s.name == 'Ex-Employee'):
                app_ids.write({'call_campaign':s.id, 'is_ex_employee': True})

        self.env['employee.resignation.details'].create({
            'applicant_id': app_ids.id,
            'resignation_date': self.resignation_date,
            'resignation_reason': self.resignation_reason
            })

        return {'type': 'ir.actions.act_window_close'}

