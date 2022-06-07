# -*- coding: utf-8 -*-
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2017 ThinkOpen Solutions (<https://tkobr.com>).
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import base64
import logging
import psycopg2
from odoo import _, api, fields, models
from odoo import tools
from odoo.addons.base.models.ir_mail_server import MailDeliveryException
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)


class res_company(models.Model):
    _inherit = "res.company"

    default_cc = fields.Many2many('res.partner', 'rel_cc_partner_ids', 'company_id', 'partner_cc_id', string="Default CC")
    default_bcc = fields.Many2many('res.partner', 'rel_bcc_partner_ids', 'company_id', 'partner_bcc_id', string="Default BCC")
    is_cc_visible = fields.Boolean(string="CC Visible", default=True)
    is_bcc_visible = fields.Boolean(string="BCC Visible", default=True)


class MailComposer(models.TransientModel):
    _inherit = 'mail.compose.message'

    def _get_default_cc_ids(self):
        if self.env.user.company_id.default_cc:
            return self.env.user.company_id.default_cc.ids

    def _get_default_bcc_ids(self):
        bcc_ids = []
        if self.env.user.company_id.default_bcc:
            bcc_ids.append(self.env.user.company_id.default_bcc.ids)
        bcc_ids.append(self.env.user.partner_id.id)
        return bcc_ids

    def _get_default_cc(self):
        if self.env.user.company_id.is_cc_visible:
            return True

    def _get_default_bcc(self):
        if self.env.user.company_id.is_bcc_visible:
            return True

    email_cc_ids = fields.Many2many(
        'res.partner', 'mail_compose_message_res_partner_cc_rel',
        'wizard_id', 'partner_cc_id', 'Email cc')
    # email_cc_ids = fields.Many2many('res.partner', 'mail_compose_message_res_partner_cc_rel', 'wizard_id', 'partner_cc_id', string='Email CC', default=_get_default_cc_ids)
    email_bcc_ids = fields.Many2many('res.partner', 'mail_compose_message_res_partner_bcc_rel', 'wizard_id', 'partner_bcc_id', string='Email BCC', default=_get_default_bcc_ids)
    is_cc = fields.Boolean(default=_get_default_cc)
    is_bcc = fields.Boolean(default=_get_default_bcc)


    @api.model
    def get_record_data(self, values):
        """ Returns a defaults-like dict with initial values for the composition
        wizard when sending an email related a previous email (parent_id) or
        a document (model, res_id). This is based on previously computed default
        values. """
        result, subject = {}, False
        if values.get('parent_id'):
            parent = self.env['mail.message'].browse(values.get('parent_id'))
            result['record_name'] = parent.record_name,
            subject = tools.ustr(parent.subject or parent.record_name or '')
            if not values.get('model'):
                result['model'] = parent.model
            if not values.get('res_id'):
                result['res_id'] = parent.res_id
            partner_ids = values.get('partner_ids', list()) + parent.partner_ids.ids
            email_cc_ids = values.get('email_cc_ids', list()) + parent.email_cc_ids.ids
            result['email_cc_ids'] = email_cc_ids
            result['partner_ids'] = partner_ids
        elif values.get('model') and values.get('res_id'):
            doc_name_get = self.env[values.get('model')].browse(values.get('res_id')).name_get()
            result['record_name'] = doc_name_get and doc_name_get[0][1] or ''
            subject = tools.ustr(result['record_name'])

        re_prefix = _('Re:')
        if subject and not (subject.startswith('Re:') or subject.startswith(re_prefix)):
            subject = "%s %s" % (re_prefix, subject)
        result['subject'] = subject

        return result
    # @api.multi
    # def get_mail_values(self, res_ids):
    #     res = super(MailComposer, self).get_mail_values(res_ids)
    #     for key, value in res.iteritems():
    #         if self.email_bcc_ids:
    #             # value['email_bcc'] = wizard.email_bcc_ids[0].email
    #             value['email_bcc_ids'] = [(4, partner_bcc.id) for partner_bcc in self.email_bcc_ids]
    #         if self.email_cc_ids:
    #             # value['email_cc'] = wizard.email_cc_ids[0].email
    #             value['email_cc_ids'] = [(4, partner_cc.id) for partner_cc in self.email_cc_ids]
    #     return res

    def get_mail_values(self, res_ids):
        """Generate the values that will be used by send_mail to create mail_messages
        or mail_mails. """
        self.ensure_one()
        results = dict.fromkeys(res_ids, False)
        rendered_values = {}
        mass_mail_mode = self.composition_mode == 'mass_mail'

        # render all template-based value at once
        if mass_mail_mode and self.model:
            rendered_values = self.render_message(res_ids)
        # compute alias-based reply-to in batch
        reply_to_value = dict.fromkeys(res_ids, None)
        if mass_mail_mode and not self.no_auto_thread:
            records = self.env[self.model].browse(res_ids)
            reply_to_value = self.env['mail.thread']._notify_get_reply_to_on_records(default=self.email_from, records=records)

        blacklisted_rec_ids = set()
        if mass_mail_mode and issubclass(type(self.env[self.model]), self.pool['mail.thread.blacklist']):
            self.env['mail.blacklist'].flush(['email'])
            self._cr.execute("SELECT email FROM mail_blacklist")
            blacklist = {x[0] for x in self._cr.fetchall()}
            if blacklist:
                targets = self.env[self.model].browse(res_ids).read(['email_normalized'])
                # First extract email from recipient before comparing with blacklist
                blacklisted_rec_ids.update(target['id'] for target in targets
                                           if target['email_normalized'] in blacklist)

        for res_id in res_ids:
            # static wizard (mail.message) values
            mail_values = {
                'subject': self.subject,
                'body': self.body or '',
                'parent_id': self.parent_id and self.parent_id.id,
                'partner_ids': [partner.id for partner in self.partner_ids],
                'attachment_ids': [attach.id for attach in self.attachment_ids],
                'email_cc_ids': [partner.id for partner in self.email_cc_ids],
                'email_bcc_ids': [partner.id for partner in self.email_bcc_ids],
                'author_id': self.author_id.id,
                'email_from': self.email_from,
                'record_name': self.record_name,
                'no_auto_thread': self.no_auto_thread,
                'mail_server_id': self.mail_server_id.id,
                'mail_activity_type_id': self.mail_activity_type_id.id,
            }

            # mass mailing: rendering override wizard static values
            if mass_mail_mode and self.model:
                record = self.env[self.model].browse(res_id)
                mail_values['headers'] = record._notify_email_headers()
                # keep a copy unless specifically requested, reset record name (avoid browsing records)
                mail_values.update(notification=not self.auto_delete_message, model=self.model, res_id=res_id, record_name=False)
                # auto deletion of mail_mail
                if self.auto_delete or self.template_id.auto_delete:
                    mail_values['auto_delete'] = True
                # rendered values using template
                email_dict = rendered_values[res_id]
                mail_values['partner_ids'] += email_dict.pop('partner_ids', [])
                mail_values['email_cc_ids'] += email_dict.pop('email_cc_ids', [])
                mail_values['email_bcc_ids'] += email_dict.pop('email_bcc_ids', [])
                mail_values.update(email_dict)
                if not self.no_auto_thread:
                    mail_values.pop('reply_to')
                    if reply_to_value.get(res_id):
                        mail_values['reply_to'] = reply_to_value[res_id]
                if self.no_auto_thread and not mail_values.get('reply_to'):
                    mail_values['reply_to'] = mail_values['email_from']
                # mail_mail values: body -> body_html, partner_ids -> recipient_ids
                mail_values['body_html'] = mail_values.get('body', '')
                mail_values['recipient_ids'] = [(4, id) for id in mail_values.pop('partner_ids', [])]
                mail_values['email_bcc'] = [(4, id) for id in mail_values.pop('email_bcc_ids', [])]
    #     # if self.email_cc_ids:
                mail_values['email_cc'] = self.email_cc_ids[0].email
                # mail_values['email_cc'] = [(4, id) for id in mail_values.pop('email_cc_ids', [])]
                # process attachments: should not be encoded before being processed by message_post / mail_mail create
                mail_values['attachments'] = [(name, base64.b64decode(enc_cont)) for name, enc_cont in email_dict.pop('attachments', list())]
                attachment_ids = []
                for attach_id in mail_values.pop('attachment_ids'):
                    new_attach_id = self.env['ir.attachment'].browse(attach_id).copy({'res_model': self._name, 'res_id': self.id})
                    attachment_ids.append(new_attach_id.id)
                attachment_ids.reverse()
                mail_values['attachment_ids'] = self.env['mail.thread']._message_post_process_attachments(
                    mail_values.pop('attachments', []),
                    attachment_ids,
                    {'model': 'mail.message', 'res_id': 0}
                )['attachment_ids']
                # Filter out the blacklisted records by setting the mail state to cancel -> Used for Mass Mailing stats
                if res_id in blacklisted_rec_ids:
                    mail_values['state'] = 'cancel'
                    # Do not post the mail into the recipient's chatter
                    mail_values['notification'] = False

            results[res_id] = mail_values
            print("XXXX ", results)
        return results



    # def get_mail_values(self, res_ids):
    #     """Generate the values that will be used by send_mail to create mail_messages
    #     or mail_mails. """
    #     self.ensure_one()
    #     results = dict.fromkeys(res_ids, False)
    #     rendered_values = {}
    #     mass_mail_mode = self.composition_mode == 'mass_mail'

    #     # render all template-based value at once
    #     if mass_mail_mode and self.model:
    #         rendered_values = self.render_message(res_ids)
    #     # compute alias-based reply-to in batch
    #     reply_to_value = dict.fromkeys(res_ids, None)
    #     if mass_mail_mode and not self.no_auto_thread:
    #         records = self.env[self.model].browse(res_ids)
    #         reply_to_value = self.env['mail.thread']._notify_get_reply_to_on_records(default=self.email_from, records=records)

    #     blacklisted_rec_ids = set()
    #     if mass_mail_mode and issubclass(type(self.env[self.model]), self.pool['mail.thread.blacklist']):
    #         self.env['mail.blacklist'].flush(['email'])
    #         self._cr.execute("SELECT email FROM mail_blacklist")
    #         blacklist = {x[0] for x in self._cr.fetchall()}
    #         if blacklist:
    #             targets = self.env[self.model].browse(res_ids).read(['email_normalized'])
    #             # First extract email from recipient before comparing with blacklist
    #             blacklisted_rec_ids.update(target['id'] for target in targets
    #                                        if target['email_normalized'] in blacklist)



    #     for res_id in res_ids:
    #         # static wizard (mail.message) values
    #         mail_values = {
    #             'subject': self.subject,
    #             'body': self.body or '',
    #             'parent_id': self.parent_id and self.parent_id.id,
    #             'partner_ids': [partner.id for partner in self.partner_ids],
    #             'attachment_ids': [attach.id for attach in self.attachment_ids],
    #             'author_id': self.author_id.id,
    #             'email_from': self.email_from,
    #             'email_cc_ids': [partner.id for partner in self.email_cc_ids],
    #             'email_bcc_ids': [partner.id for partner in self.email_bcc_ids],
    #             'record_name': self.record_name,
    #             'no_auto_thread': self.no_auto_thread,
    #             'mail_server_id': self.mail_server_id.id,
    #             'mail_activity_type_id': self.mail_activity_type_id.id,
    #         }

    #         # mass mailing: rendering override wizard static values
    #         if mass_mail_mode and self.model:
    #             record = self.env[self.model].browse(res_id)
    #             mail_values['headers'] = record._notify_email_headers()
    #             # keep a copy unless specifically requested, reset record name (avoid browsing records)
    #             mail_values.update(notification=not self.auto_delete_message, model=self.model, res_id=res_id, record_name=False)
    #             # auto deletion of mail_mail
    #             if self.auto_delete or self.template_id.auto_delete:
    #                 mail_values['auto_delete'] = True
    #             # rendered values using template
    #             email_dict = rendered_values[res_id]
    #             mail_values['partner_ids'] += email_dict.pop('partner_ids', [])
    #             mail_values['email_cc_ids'] += email_dict.pop('email_cc_ids', [])
    #             mail_values['email_bcc_ids'] += email_dict.pop('email_bcc_ids', [])
    #             mail_values.update(email_dict)
    #             if not self.no_auto_thread:
    #                 mail_values.pop('reply_to')
    #                 if reply_to_value.get(res_id):
    #                     mail_values['reply_to'] = reply_to_value[res_id]
    #             if self.no_auto_thread and not mail_values.get('reply_to'):
    #                 mail_values['reply_to'] = mail_values['email_from']
    #             # mail_mail values: body -> body_html, partner_ids -> recipient_ids
    #             mail_values['body_html'] = mail_values.get('body', '')
    #             mail_values['recipient_ids'] = [(4, id) for id in mail_values.pop('partner_ids', [])]
    #     # if self.email_bcc_ids:
    #         # value['email_bcc'] = wizard.email_bcc_ids[0].email
    #             mail_values['email_bcc'] = [(4, id) for id in mail_values.pop('email_bcc_ids', [])]
    #     # if self.email_cc_ids:
    #         # value['email_cc'] = wizard.email_cc_ids[0].email
    #             mail_values['email_cc'] = [(4, id) for id in mail_values.pop('email_cc_ids', [])]
    #             print("xxxxxxxxxxxxxxxxxxyyyy  ",mail_values['email_cc'])
    #             # process attachments: should not be encoded before being processed by message_post / mail_mail create
    #             mail_values['attachments'] = [(name, base64.b64decode(enc_cont)) for name, enc_cont in email_dict.pop('attachments', list())]
    #             attachment_ids = []
    #             for attach_id in mail_values.pop('attachment_ids'):
    #                 new_attach_id = self.env['ir.attachment'].browse(attach_id).copy({'res_model': self._name, 'res_id': self.id})
    #                 attachment_ids.append(new_attach_id.id)
    #             attachment_ids.reverse()
    #             mail_values['attachment_ids'] = self.env['mail.thread']._message_post_process_attachments(
    #                 mail_values.pop('attachments', []),
    #                 attachment_ids,
    #                 {'model': 'mail.message', 'res_id': 0}
    #             )['attachment_ids']
    #             # Filter out the blacklisted records by setting the mail state to cancel -> Used for Mass Mailing stats
    #             if res_id in blacklisted_rec_ids:
    #                 mail_values['state'] = 'cancel'
    #                 # Do not post the mail into the recipient's chatter
    #                 mail_values['notification'] = False

    #         results[res_id] = mail_values
    #     return results

class Message(models.Model):
    _inherit = 'mail.message'

    email_cc_ids = fields.Many2many('res.partner', 'mail_notification_cc', 'message_id', 'partner_id', string='CC',
        help='Partners that have a notification pushing this message in their mailboxes')
    email_bcc_ids = fields.Many2many('res.partner', 'mail_notification_bcc', 'message_id', 'partner_id', string='BCC',
        help='Partners that have a notification pushing this message in their mailboxes')

    # @api.multi
    def _notify(self, force_send=False, send_after_commit=True, user_signature=True):
        """ Add the related record followers to the destination partner_ids if is not a private message.
            Call mail_notification.notify to manage the email sending
        """
        group_user = self.env.ref('base.group_user')
        # have a sudoed copy to manipulate partners (public can go here with 
        # website modules like forum / blog / ...
        self_sudo = self.sudo()

        # TDE CHECK: add partners / channels as arguments to be able to notify a message with / without computation ??
        self.ensure_one()  # tde: not sure, just for testinh, will see
        partners = self.env['res.partner'] | self.partner_ids
        channels = self.env['mail.channel'] | self.channel_ids

        # all followers of the mail.message document have to be added as partners and notified
        # and filter to employees only if the subtype is internal
        if self_sudo.subtype_id and self.model and self.res_id:
            followers = self.env['mail.followers'].sudo().search([
                ('res_model', '=', self.model),
                ('res_id', '=', self.res_id)
            ]).filtered(lambda fol: self.subtype_id in fol.subtype_ids)
            if self_sudo.subtype_id.internal:
                followers = followers.filtered(lambda fol: fol.channel_id or (fol.partner_id.user_ids and group_user in fol.partner_id.user_ids[0].mapped('groups_id')))
            channels = self_sudo.channel_ids | followers.mapped('channel_id')
            partners = self_sudo.partner_ids | followers.mapped('partner_id')
        else:
            channels = self_sudo.channel_ids
            partners = self_sudo.partner_ids

        # if self.email_cc_ids:
        #     partners |= self.email_cc_ids
        # if self.email_bcc_ids:
        #     partners |= self.email_bcc_ids

        # remove author from notified partners
        if not self._context.get('mail_notify_author', False) and self_sudo.author_id:
            partners = partners - self_sudo.author_id

        # update message, with maybe custom values
        message_values = {
            'channel_ids': [(6, 0, channels.ids)],
            'needaction_partner_ids': [(6, 0, partners.ids)]
        }
        if self.model and self.res_id and hasattr(self.env[self.model], 'message_get_message_notify_values'):
            message_values.update(self.env[self.model].browse(self.res_id).message_get_message_notify_values(self, message_values))
        self.write(message_values)
        # notify partners and channels
        partners._notify(self, force_send=force_send, send_after_commit=send_after_commit, user_signature=user_signature)
        channels._notify(self)

        # Discard cache, because child / parent allow reading and therefore
        # change access rights.
        if self.parent_id:
            self.parent_id.invalidate_cache()

        return True


class MailMail(models.Model):
    _inherit = 'mail.mail'

    email_bcc = fields.Char(string='Bcc', help='Black Carbon copy message recipients')

    def _send_prepare_values(self, partner=None):
        """Return a dictionary for specific email values, depending on a
        partner, or generic to the whole recipients given by mail.email_to.

            :param Model partner: specific recipient partner
        """
        self.ensure_one()
        body = self._send_prepare_body()
        body_alternative = tools.html2plaintext(body)
        if partner:
            email_to = [tools.formataddr((partner.name or 'False', partner.email or 'False'))]
            email_cc = [tools.formataddr((partner.name or 'False', partner.email or 'False'))]
            email_bcc = [tools.formataddr((partner.name or 'False', partner.email or 'False'))]
        else:
            email_to = tools.email_split_and_format(self.email_to)
            email_cc = tools.email_split_and_format(self.email_cc)
            email_bcc = tools.email_split_and_format(self.email_bcc)
        res = {
            'body': body,
            'body_alternative': body_alternative,
            'email_to': email_to,
            'email_cc': email_cc,
            'email_bcc': email_bcc,
        }
        return res

    def _send(self, auto_commit=False, raise_exception=False, smtp_session=None):
        IrMailServer = self.env['ir.mail_server']
        IrAttachment = self.env['ir.attachment']
        for mail_id in self.ids:
            success_pids = []
            failure_type = None
            processing_pid = None
            mail = None
            try:
                mail = self.browse(mail_id)
                if mail.state != 'outgoing':
                    if mail.state != 'exception' and mail.auto_delete:
                        mail.sudo().unlink()
                    continue

                # remove attachments if user send the link with the access_token
                body = mail.body_html or ''
                attachments = mail.attachment_ids
                for link in re.findall(r'/web/(?:content|image)/([0-9]+)', body):
                    attachments = attachments - IrAttachment.browse(int(link))

                # load attachment binary data with a separate read(), as prefetching all
                # `datas` (binary field) could bloat the browse cache, triggerring
                # soft/hard mem limits with temporary data.
                attachments = [(a['name'], base64.b64decode(a['datas']), a['mimetype'])
                               for a in attachments.sudo().read(['name', 'datas', 'mimetype']) if a['datas'] is not False]

                # specific behavior to customize the send email for notified partners
                email_list = []
                if mail.email_to:
                    email_list.append(mail._send_prepare_values())
                for partner in mail.recipient_ids:
                    values = mail._send_prepare_values(partner=partner)
                    values['partner_id'] = partner
                    email_list.append(values)

                # headers
                headers = {}
                ICP = self.env['ir.config_parameter'].sudo()
                bounce_alias = ICP.get_param("mail.bounce.alias")
                catchall_domain = ICP.get_param("mail.catchall.domain")
                if bounce_alias and catchall_domain:
                    if mail.mail_message_id.is_thread_message():
                        headers['Return-Path'] = '%s+%d-%s-%d@%s' % (bounce_alias, mail.id, mail.model, mail.res_id, catchall_domain)
                    else:
                        headers['Return-Path'] = '%s+%d@%s' % (bounce_alias, mail.id, catchall_domain)
                if mail.headers:
                    try:
                        headers.update(safe_eval(mail.headers))
                    except Exception:
                        pass

                # Writing on the mail object may fail (e.g. lock on user) which
                # would trigger a rollback *after* actually sending the email.
                # To avoid sending twice the same email, provoke the failure earlier
                mail.write({
                    'state': 'exception',
                    'failure_reason': _('Error without exception. Probably due do sending an email without computed recipients.'),
                })
                # Update notification in a transient exception state to avoid concurrent
                # update in case an email bounces while sending all emails related to current
                # mail record.
                notifs = self.env['mail.notification'].search([
                    ('notification_type', '=', 'email'),
                    ('mail_id', 'in', mail.ids),
                    ('notification_status', 'not in', ('sent', 'canceled'))
                ])
                if notifs:
                    notif_msg = _('Error without exception. Probably due do concurrent access update of notification records. Please see with an administrator.')
                    notifs.sudo().write({
                        'notification_status': 'exception',
                        'failure_type': 'UNKNOWN',
                        'failure_reason': notif_msg,
                    })
                    # `test_mail_bounce_during_send`, force immediate update to obtain the lock.
                    # see rev. 56596e5240ef920df14d99087451ce6f06ac6d36
                    notifs.flush(fnames=['notification_status', 'failure_type', 'failure_reason'], records=notifs)

                # build an RFC2822 email.message.Message object and send it without queuing
                res = None
                for email in email_list:
                    msg = IrMailServer.build_email(
                        email_from=mail.email_from,
                        email_to=email.get('email_to'),
                        subject=mail.subject,
                        body=email.get('body'),
                        body_alternative=email.get('body_alternative'),
                        email_cc=tools.email_split(mail.email_cc),
                        email_bcc=tools.email_split(mail.email_bcc),
                        reply_to=mail.reply_to,
                        attachments=attachments,
                        message_id=mail.message_id,
                        references=mail.references,
                        object_id=mail.res_id and ('%s-%s' % (mail.res_id, mail.model)),
                        subtype='html',
                        subtype_alternative='plain',
                        headers=headers)
                    processing_pid = email.pop("partner_id", None)
                    try:
                        res = IrMailServer.send_email(
                            msg, mail_server_id=mail.mail_server_id.id, smtp_session=smtp_session)
                        if processing_pid:
                            success_pids.append(processing_pid)
                        processing_pid = None
                    except AssertionError as error:
                        if str(error) == IrMailServer.NO_VALID_RECIPIENT:
                            failure_type = "RECIPIENT"
                            # No valid recipient found for this particular
                            # mail item -> ignore error to avoid blocking
                            # delivery to next recipients, if any. If this is
                            # the only recipient, the mail will show as failed.
                            _logger.info("Ignoring invalid recipients for mail.mail %s: %s",
                                         mail.message_id, email.get('email_to'))
                        else:
                            raise
                if res:  # mail has been sent at least once, no major exception occured
                    mail.write({'state': 'sent', 'message_id': res, 'failure_reason': False})
                    _logger.info('Mail with ID %r and Message-Id %r successfully sent', mail.id, mail.message_id)
                    # /!\ can't use mail.state here, as mail.refresh() will cause an error
                    # see revid:odo@openerp.com-20120622152536-42b2s28lvdv3odyr in 6.1
                mail._postprocess_sent_message(success_pids=success_pids, failure_type=failure_type)
            except MemoryError:
                # prevent catching transient MemoryErrors, bubble up to notify user or abort cron job
                # instead of marking the mail as failed
                _logger.exception(
                    'MemoryError while processing mail with ID %r and Msg-Id %r. Consider raising the --limit-memory-hard startup option',
                    mail.id, mail.message_id)
                # mail status will stay on ongoing since transaction will be rollback
                raise
            except (psycopg2.Error, smtplib.SMTPServerDisconnected):
                # If an error with the database or SMTP session occurs, chances are that the cursor
                # or SMTP session are unusable, causing further errors when trying to save the state.
                _logger.exception(
                    'Exception while processing mail with ID %r and Msg-Id %r.',
                    mail.id, mail.message_id)
                raise
            except Exception as e:
                failure_reason = tools.ustr(e)
                _logger.exception('failed sending mail (id: %s) due to %s', mail.id, failure_reason)
                mail.write({'state': 'exception', 'failure_reason': failure_reason})
                mail._postprocess_sent_message(success_pids=success_pids, failure_reason=failure_reason, failure_type='UNKNOWN')
                if raise_exception:
                    if isinstance(e, (AssertionError, UnicodeEncodeError)):
                        if isinstance(e, UnicodeEncodeError):
                            value = "Invalid text: %s" % e.object
                        else:
                            # get the args of the original error, wrap into a value and throw a MailDeliveryException
                            # that is an except_orm, with name and value as arguments
                            value = '. '.join(e.args)
                        raise MailDeliveryException(_("Mail Delivery Failed"), value)
                    raise

            if auto_commit is True:
                self._cr.commit()
        return True


class Partner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def _notify_prepare_email_values(self, message):
        mail_values = super(Partner, self)._notify_prepare_email_values(message)
        cc_email_list = message.email_cc_ids.mapped('email')
        bcc_email_list = message.email_bcc_ids.mapped('email')
        cc_bcc = {
            'email_cc': ",".join(cc_email_list),
            'email_bcc': ",".join(bcc_email_list),
        }
        mail_values.update(cc_bcc)
        return mail_values
