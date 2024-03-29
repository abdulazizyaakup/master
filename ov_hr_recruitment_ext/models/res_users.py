# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model
    def _default_map_website(self):
        return self.env['map.website'].search([
            '|', ('address_url', '!=', False), ('lat_lon_url', '!=', False)],
            limit=1)

    @api.model
    def _default_route_map_website(self):
        return self.env['map.website'].search([
            '|', ('route_address_url', '!=', False),
            ('route_lat_lon_url', '!=', False)], limit=1)

    # begin with context_ to allow user to change it by himself
    context_map_website_id = fields.Many2one(
        'map.website', string='Map Website', default=_default_map_website,
        domain=['|', ('address_url', '!=', False),
                ('lat_lon_url', '!=', False)])
    # We want to give the possibility to the user to have one map provider for
    # regular maps and another one for routing
    context_route_map_website_id = fields.Many2one(
        'map.website', string='Route Map Website',
        domain=['|', ('route_address_url', '!=', False),
                ('route_lat_lon_url', '!=', False)],
        default=_default_route_map_website,
        help="Map provided used when you click on the car icon on the partner "
             "form to display an itinerary.")
    # context_route_start_partner_id = fields.Many2one(
    #     'res.partner', string='Start Address for Route Map')

    @api.model
    def create(self, vals):
        """On creation, if no starting partner is provided, assign the current
        created one.
        """
        user = super(ResUsers, self).create(vals)
        if not vals.get('context_route_start_partner_id'):
            user.context_route_start_partner_id = user.partner_id.id
        return user
