# -*- coding: utf-8 -*-
from odoo import api, fields, models


class TravelNote(models.Model):
    _name = 'travel.note'
    _description = 'Trip Note / Journal Entry'
    _order = 'date desc, create_date desc'

    name = fields.Char(string='Title', required=True)
    trip_id = fields.Many2one('travel.trip', string='Trip', required=True, ondelete='cascade')
    stop_id = fields.Many2one('travel.stop', string='Related Stop',
                              domain="[('trip_id', '=', trip_id)]")
    date = fields.Date(string='Date', default=fields.Date.context_today)
    content = fields.Html(string='Content')
    note_type = fields.Selection([
        ('general', 'General Note'),
        ('reminder', 'Reminder'),
        ('booking', 'Booking Info'),
        ('contact', 'Contact Info'),
        ('tip', 'Travel Tip'),
        ('journal', 'Journal Entry'),
    ], string='Type', default='general')
    is_important = fields.Boolean(string='Important', default=False)
