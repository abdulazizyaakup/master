# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import datetime
from datetime import datetime, timedelta
from werkzeug import urls
import functools
import urllib
import requests
import re
from jinja2 import Template
from dateutil import parser

try:
    from jinja2.sandbox import SandboxedEnvironment
    mako_template_env = SandboxedEnvironment(
        block_start_string="<%",
        block_end_string="%>",
        variable_start_string="${",
        variable_end_string="}",
        comment_start_string="<%doc>",
        comment_end_string="</%doc>",
        line_statement_prefix="%",
        line_comment_prefix="##",
        trim_blocks=True,               # do not output newline after blocks
        autoescape=True,                # XML/HTML automatic escaping
    )
    mako_template_env.globals.update({
        'str': str,
        'quote': urls.url_quote,
        'urlencode': urls.url_encode,
        'datetime': datetime,
        'len': len,
        'abs': abs,
        'min': min,
        'max': max,
        'sum': sum,
        'filter': filter,
        'reduce': functools.reduce,
        'map': map,
        'round': round,

        'relativedelta': lambda *a, **kw : relativedelta.relativedelta(*a, **kw),
    })
except ImportError:
    _logger.warning("jinja2 not available, templating features will not work!")

#from datetime import datetime
# date = datetime.strptime('26 Sep 2012', '%d %b %Y')
# newdate = date.replace(hour=11, minute=59)


class TenderPartner(models.Model):
    _inherit = 'res.partner'

    def _default_past_date(self):
        current_date = datetime.now()
        now_minus_12 = datetime.now() - timedelta(hours=24)
        new_now_minus_12 = now_minus_12.replace(hour=10, minute=00)
        return new_now_minus_12

    def _default_future_date(self):
        current_date = datetime.now()
        now_plus_12 = datetime.now() + timedelta(hours=24)
        new_now_plus_12 = now_plus_12.replace(hour=10, minute=00)
        return new_now_plus_12

    def _default_current_date(self):
        current_date = datetime.now()
        return current_date

    def _default_end_date(self):
        return self.get_end_date()


    tb = fields.Boolean("Tenderboard Customer?", default=False)
    test = fields.Char("Test")
    keys = fields.Char("Keys")
    keywords_ids = fields.Many2many('ov.keyword','ov_keyword_res_partner_rel', 'res_partner_id', 'ov_keyword_id', string='Keywords')
    tender_ids = fields.Many2many('ov.tender','ov_tender_res_partner_rel', 'res_partner_id', 'ov_tender_id', string="Tenders")
    tender_line = fields.One2many('ov.tender', 'tender_id', string="Tenders")
    tenders_count = fields.Integer("Tenders Count", compute="_compute_tenders_count")
    today_tenders_count = fields.Integer("Today Tenders Count", compute="_compute_today_tenders_count")
    today_date = fields.Datetime(string="Today Date", default=_default_current_date,required=True)
    #sub_end_date = fields.Datetime(string="Subscription End Date", default=_default_end_date)
    p_date = fields.Datetime(string="Previous Date", default=_default_past_date,required=True)
    f_date = fields.Datetime(string="Next Date", default=_default_future_date,required=True)
    is_date_compare = fields.Integer("Date Compare", compute="get_end_date")

    #_sql_constraints = [('email', 'UNIQUE (email)',  'Email exist. Please enter another email!')]

    def init(self):
        fields = ("keywords_ids", "tb", "keys", "keywords_ids","res_partner_id","ov_tender_id")
        self.env.cr.execute(
            "UPDATE ir_model_fields  SET website_form_blacklisted=false WHERE model=%s AND name in %s", ('res.partner', tuple(fields)))

    @api.multi
    def get_end_date(self):
        current_date = datetime.today().strftime('%Y-%m-%d')
        new_current_date = datetime.strptime(current_date, '%Y-%m-%d').date()
        partner = self.env['sale.subscription'].search([])
        #partner2 = self.env['res.partner'].search([('tb','=',True)])
        for pa in partner:
            val1 = pa.recurring_next_date
            val2 = pa.partner_id
            if (new_current_date <= val1):
                val2.is_date_compare = 1
            else:
                val2.is_date_compare = 0

    @api.multi
    def insert_val(self):
        #import pdb; pdb.set_trace()
        self.env.cr.execute("DELETE FROM ov_tender_res_partner_rel")
        result = []
        partner_ids = self.env['res.partner'].search([('tb', '=', True)])
        partner_key_ids = self.env['res.partner'].browse(self._context.get('keywords_ids'))
        keyword = self.env['ov.keyword'].search([('name', '!=', False)])
        tender = self.env['ov.tender'].search([('name', '!=', False)])

        def check_all(sentence, ws):
            return all((w.lower() in sentence.lower() for w in ws))

        keys = []
        for k in keyword:
            keys.append(k.name)
        pkey_id = []
        pkey_name = []
        for t in tender:
            for p in partner_ids:
                for pk in p.keywords_ids:
                    pkey_id.append(pk.id)
                    pkey_name.append(pk.name)
                    if(pk.name):
                        pk_name = pk.name
                        pk_name_list = pk_name.split(" ")
                        pk_words = pk_name_list
                        t_name = t.description
                        t_name_list = t_name.split(" ")
                        t_words = t_name_list

                        if (t.category in pk.name):
                            val = t.id
                            self.env.cr.execute("INSERT INTO ov_tender_res_partner_rel (ov_tender_id, res_partner_id) VALUES ('%s','%s') ON CONFLICT (ov_tender_id, res_partner_id) DO NOTHING"%(val,p.id))
                    
                        for pk_vals in pk_words:
                            for t_vals in t_words:
                                skip_word = ["and","or","the","of","for","at","on"]
                                #if any(check_all(t_vals, word.split('+')) for word in words):
                                if((pk_vals in skip_word) or (t_vals in skip_word)):
                                    pass
                                if any(check_all(t_vals, word.split('+')) for word in pk_words):
                                    val_with_word_check = t.id
                                    self.env.cr.execute("INSERT INTO ov_tender_res_partner_rel (ov_tender_id, res_partner_id) VALUES ('%s','%s') ON CONFLICT (ov_tender_id, res_partner_id) DO NOTHING"%(val_with_word_check,p.id))



#    @api.depends('tender_ids')
#    def _compute_today_tenders_count(self):
#        for tender in self:
#            for t in tender.tender_ids:
#                if (t.is_included == 1):
#                    tender.today_tenders_count = len(t)

    @api.depends('tender_ids')
    def _compute_tenders_count(self):
        for tender in self:
            tender.tenders_count = len(tender.tender_ids)

    @api.depends('tender_ids')
    def _compute_today_tenders_count(self):
        current_date = datetime.now()
        now_minus_12 = datetime.now() - timedelta(hours=12)
        now_plus_12 = datetime.now() + timedelta(hours=12)
        for tender in self:
            sum = 0
            for t in tender.tender_ids:
                tend_start_date = t.start_date
                difference = current_date - tend_start_date
                #if (t.is_included == 1):
                    #if ((tend_start_date < now_plus_12)&(tend_start_date > now_minus_12)):
                     #difference = current_date - tend_start_date
                if ((difference.days == 0) or (difference.days == -1)) :
                    sum = sum + len(t)
                    #print
            tender.today_tenders_count = sum

    @api.model
    def _keyword_to_write_vals(self, tags=''):
        Tag = self.env['ov.keyword']
        keywords_ids = []
        existing_keep = []
        user = self.env.user
        for tag in (tag for tag in tags.split(',') if tag):
            if tag.startswith('_'):  # it's a new tag
                # check that not arleady created meanwhile or maybe excluded by the limit on the search
                tag_ids = Tag.search([('name', '=', tag[1:])])
                if tag_ids:
                    existing_keep.append(int(tag_ids[0]))
                else:
                    keywords_ids.append((0, 0, {'name': tag[1:], 'partner_id': self.id}))
            else:
               existing_keep.append(int(tag))
        keywords_ids.insert(0, [6, 0, existing_keep])
        return keywords_ids

    @api.model
    def _email_to_write_vals(self, email=''):
        emails = []
        pemail = self.env['res.partner']

        for p in pemail:
            if p:
                emails.append(p.email)

        return emails

    #PENDING ON THIS CHECK END DATE
    def check_date_period(self):
        #if now-timedelta(hours=24) <= set_date <= now+timedelta(hours=24):
        current_date = datetime.now()
        partner_ids = self.env['res.partner'].search([('tb', '=', True)])
        for tend in partner_ids:
            for t in tend.tender_ids:
                s_date = t.start_date
                #print("ID :", tend.id ," START DATE :",s_date)

                difference = current_date - s_date
                # print(difference)
                if difference.days == 0:
                    print("ID :", tend.id , "CURRENT :", current_date ," START DATE :",s_date, " IS WITHIN 24 HOURS ", difference)
                if difference.days != 0:
                    print("ID :", tend.id , "CURRENT :", current_date ," START DATE :",s_date, " IS NOT WITHIN 24 HOURS ", difference)

                    #print("date is within 24 hours")
        # now_minus_12 = datetime.now() - timedelta(hours=24)
        # now_minus_36 = datetime.now() - timedelta(hours=36)

        # difference = current_date - now_minus_12

        # if difference.days == 0:
        #     print("date is within 24 hours")
        # if difference2.days != 0:
        #     print("date is within 24 hours")

        ## Also you can check the difference between two dates in seconds
        #total_seconds = (difference.days * 24 * 60 * 60) + difference.seconds


    # def _get_subscription_date(self):
    #     current_date = datetime.now()
    #     partner = self.env['sale.subscription'].search([('partner_id', '=', self.id)])
    #     for v in partner:
    #         if (v.date < current_date):
    #             pass
    #         else:
    #             self.sub_end_date = v.date

    # @api.depends('tender_ids')
    # def _compute_tenders_count(self):
    #     current_date = datetime.now()
    #     for tender in self:
    #         tender.tenders_count = len(tender.tender_ids)
