# -*- coding: utf-8 -*-
from odoo import api, fields, models


class TravelActivity(models.Model):
    _name = 'travel.activity'
    _description = 'Travel Activity'
    _order = 'date, time_start'

    name = fields.Char(string='Activity Name', required=True)
    description = fields.Html(string='Description')
    image = fields.Image(string='Image', max_width=1024, max_height=768)


    stop_id = fields.Many2one('travel.stop', string='Trip Stop', ondelete='cascade')
    trip_id = fields.Many2one('travel.trip', related='stop_id.trip_id', store=True, string='Trip')
    city_id = fields.Many2one('travel.city', string='City',
                              compute='_compute_city_id', store=True, readonly=False)


    activity_type = fields.Selection([
        ('sightseeing', 'Sightseeing'),
        ('food', 'Food & Dining'),
        ('adventure', 'Adventure'),
        ('culture', 'Culture'),
        ('shopping', 'Shopping'),
        ('nightlife', 'Nightlife'),
        ('nature', 'Nature'),
        ('beach', 'Beach'),
        ('wellness', 'Wellness & Spa'),
        ('transport', 'Transport'),
        ('other', 'Other'),
    ], string='Category', default='sightseeing', required=True)


    date = fields.Date(string='Date')
    time_start = fields.Float(string='Start Time', help='Start time in 24h format (e.g. 14.5 = 2:30 PM)')
    time_end = fields.Float(string='End Time')
    duration_hours = fields.Float(string='Duration (Hours)', compute='_compute_duration', store=True)


    currency_id = fields.Many2one(related='stop_id.currency_id')
    cost = fields.Monetary(string='Cost', currency_field='currency_id')
    cost_level = fields.Selection([
        ('free', 'Free'),
        ('budget', '$ Budget'),
        ('moderate', '$$ Moderate'),
        ('expensive', '$$$ Expensive'),
    ], string='Cost Level', compute='_compute_cost_level', store=True)


    address = fields.Char(string='Address')
    website = fields.Char(string='Website')
    rating = fields.Float(string='Rating', digits=(2, 1))
    is_booked = fields.Boolean(string='Already Booked', default=False)
    booking_reference = fields.Char(string='Booking Reference')
    active = fields.Boolean(default=True)

    @api.depends('stop_id.city_id')
    def _compute_city_id(self):
        for activity in self:
            if activity.stop_id:
                activity.city_id = activity.stop_id.city_id
            elif not activity.city_id:
                activity.city_id = False

    @api.depends('time_start', 'time_end')
    def _compute_duration(self):
        for activity in self:
            if activity.time_start and activity.time_end and activity.time_end > activity.time_start:
                activity.duration_hours = activity.time_end - activity.time_start
            else:
                activity.duration_hours = 0

    @api.depends('cost')
    def _compute_cost_level(self):
        for activity in self:
            if not activity.cost or activity.cost == 0:
                activity.cost_level = 'free'
            elif activity.cost < 25:
                activity.cost_level = 'budget'
            elif activity.cost < 75:
                activity.cost_level = 'moderate'
            else:
                activity.cost_level = 'expensive'
