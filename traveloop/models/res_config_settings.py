# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    travel_default_currency_id = fields.Many2one(
        'res.currency', string='Default Travel Currency',
        config_parameter='traveloop.default_currency_id')
    travel_allow_public_sharing = fields.Boolean(
        string='Allow Public Trip Sharing',
        config_parameter='traveloop.allow_public_sharing',
        default=True)
    travel_max_stops_per_trip = fields.Integer(
        string='Max Stops per Trip',
        config_parameter='traveloop.max_stops_per_trip',
        default=20)
