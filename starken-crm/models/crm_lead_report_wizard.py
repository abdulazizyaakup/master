from odoo import api, fields, models, tools 
from odoo.exceptions import UserError
from odoo import SUPERUSER_ID
from datetime import time, timedelta, datetime, date

class ProjectReportWizard(models.TransientModel):
    _name = "crm.lead.project.report.wizard"
    _description = "CRM Project Report Wizard"

    prj_date_from = fields.Date('Date From',required=True, default=fields.Date.today().replace(month=1,day=1))
    prj_date_to = fields.Date('Date To', required=True, default=fields.Date.today().replace(month=12,day=31))
    prj_level_to_show = fields.Selection([('prj_specy', 'Specifying'), ('prj_specd', 'Specified'), ('prj_sec', 'Secure')], string='Project Level Report', default='prj_specy', required=True)

    def action_generate_report(self):
        pivot_view_ref = self.env.ref('starken-crm.crm_lead_%s_pivot'% self.prj_level_to_show, False)
        view_name = ""
        domain_to_use = ""

        if self.prj_level_to_show == 'Specifying':
            view_name = "Project Specifying Report"
            domain_to_use = "[('crm_project_level.name','=', 'Specifying'), ('crm_prj_status','!=','lost'), ('crm_prj_spcy_date','>=', '%s'),('crm_prj_spcy_date','<=','%s'),('active','=','True')]"

        elif self.prj_level_to_show == 'Specified':
            view_name = "Project Specified Report"
            domain_to_use = "['|',('active','=','True'), ('crm_project_level.name','=', 'Secured'), ('crm_project_level.name','=', 'Specified'), ('crm_prj_spcd_date','>=', '%s'),('crm_prj_spcd_date','<=','%s')]"
        else:
            view_name = "Project Secured Report"
            domain_to_use = "[('active','=','True'),('crm_project_level.name','=', 'Secured'), ('crm_prj_status','!=','lost'), ('crm_prj_sec_date','>=', '%s'),('crm_prj_sec_date','<=','%s')]"

        return {
            'name': '%s From %s To %s' % (view_name,self.prj_date_from.strftime('%d-%m-%Y'),self.prj_date_to.strftime('%d-%m-%Y')),
            'view_mode': 'pivot',
            'view_id': False,
            'res_model': 'crm.lead',
            'type': 'ir.actions.act_window',
            'target': 'main',
            'domain': domain_to_use%(self.prj_date_from.strftime('%Y-%m-%d'),self.prj_date_to.strftime('%Y-%m-%d')),
            'views' : [(pivot_view_ref and pivot_view_ref.id or False, 'pivot')],
            'context' : {}
        }