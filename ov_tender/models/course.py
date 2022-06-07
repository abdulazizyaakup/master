# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import models, fields, api, exceptions, _


class Course(models.Model):
    _name = 'openacademy.course'
    _description = "Manage Courses"
    _inherit = 'mail.thread'

    name = fields.Char(size=256, translate=True)
    description = fields.Html()
    responsible_id = fields.Many2one('res.users', ondelete='set null', string="Responsible", index=True, )
    session_ids = fields.One2many('openacademy.session', 'course_id', string="Sessions")
    level = fields.Selection([(1, 'Easy'), (2, 'Medium'), (3, 'Hard')], string="Difficulty Level")
    color = fields.Integer()
    session_count = fields.Integer("Session Count", compute="_compute_session_count")

    fname = fields.Char('Filename')
    datas = fields.Binary('File')
    currency_id = fields.Many2one('res.currency', 'Currency')
    logo = fields.Binary('Course Logo', attachment=True)

    price = fields.Monetary('Price')

    _sql_constraints = [
       ('name_description_check', 'CHECK(name != description)',
        _("The title of the course should not be the description")),

       ('name_unique', 'UNIQUE(name)',
        _("The course title must be unique")),
    ]

    @api.multi
    def copy(self, default=None):
        default = dict(default or {})

        copied_count = self.search_count(
            [('name', '=like', _(u"Copy of {}%".format(self.name)))])
        if not copied_count:
            new_name = _(u"Copy of {}").format(self.name)
        else:
            new_name = _(u"Copy of {} ({})").format(self.name, copied_count)

        default['name'] = new_name
        return super(Course, self).copy(default)

    @api.depends('session_ids')
    def _compute_session_count(self):
        for course in self:
            course.session_count = len(course.session_ids)
