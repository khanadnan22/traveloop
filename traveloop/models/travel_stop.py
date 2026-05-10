# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class TravelStop(models.Model):
    _name = 'travel.stop'
    _description = 'Travel Stop'
    _order = 'sequence, arrival_date'
    _inherit = ['mail.thread']

    name = fields.Char(string='Stop Name', compute='_compute_name', store=True, readonly=False)
    sequence = fields.Integer(string='Sequence', default=10)
    trip_id = fields.Many2one('travel.trip', string='Trip', required=True, ondelete='cascade')
    city_id = fields.Many2one('travel.city', string='City', required=True, tracking=True)
    country_id = fields.Many2one('res.country', related='city_id.country_id', store=True, string='Country')


    arrival_date = fields.Date(string='Arrival Date', required=True, tracking=True)
    departure_date = fields.Date(string='Departure Date', required=True, tracking=True)
    duration_days = fields.Integer(string='Duration (Days)', compute='_compute_duration', store=True)


    notes = fields.Html(string='Notes')
    accommodation = fields.Char(string='Accommodation')
    accommodation_cost = fields.Float(string='Accommodation Cost/Night')
    transport_mode = fields.Selection([
        ('flight', 'Flight'),
        ('train', 'Train'),
        ('bus', 'Bus'),
        ('car', 'Car'),
        ('ferry', 'Ferry'),
        ('other', 'Other'),
    ], string='Transport Mode')
    transport_cost = fields.Float(string='Transport Cost')


    activity_ids = fields.One2many('travel.activity', 'stop_id', string='Activities')
    activity_count = fields.Integer(compute='_compute_activity_count', string='Activities')


    currency_id = fields.Many2one(related='trip_id.currency_id')
    estimated_cost = fields.Monetary(string='Estimated Cost', currency_field='currency_id',
                                      compute='_compute_estimated_cost', store=True)

    _sql_constraints = [
        ('date_check', 'CHECK(departure_date >= arrival_date)', 'Departure date must be after arrival date!'),
    ]

    @api.depends('city_id')
    def _compute_name(self):
        for stop in self:
            if stop.city_id and not stop.name:
                stop.name = stop.city_id.name

    @api.depends('arrival_date', 'departure_date')
    def _compute_duration(self):
        for stop in self:
            if stop.arrival_date and stop.departure_date:
                stop.duration_days = (stop.departure_date - stop.arrival_date).days + 1
            else:
                stop.duration_days = 0

    def _compute_activity_count(self):
        for stop in self:
            stop.activity_count = len(stop.activity_ids)

    @api.depends('activity_ids.cost', 'accommodation_cost', 'duration_days', 'transport_cost')
    def _compute_estimated_cost(self):
        for stop in self:
            activity_cost = sum(stop.activity_ids.mapped('cost'))
            accommodation_total = (stop.accommodation_cost or 0) * max(stop.duration_days - 1, 1)
            stop.estimated_cost = activity_cost + accommodation_total + (stop.transport_cost or 0)

    @api.constrains('arrival_date', 'departure_date', 'trip_id')
    def _check_dates(self):
        for stop in self:
            if stop.arrival_date and stop.departure_date:
                if stop.departure_date < stop.arrival_date:
                    raise ValidationError(_('Departure date must be after arrival date.'))
                if stop.trip_id:
                    if stop.arrival_date < stop.trip_id.date_start:
                        raise ValidationError(_('Stop arrival date cannot be before trip start date.'))
                    if stop.departure_date > stop.trip_id.date_end:
                        raise ValidationError(_('Stop departure date cannot be after trip end date.'))

    def action_view_activities(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Activities at %s', self.city_id.name),
            'res_model': 'travel.activity',
            'view_mode': 'list,form',
            'domain': [('stop_id', '=', self.id)],
            'context': {
                'default_stop_id': self.id,
                'default_city_id': self.city_id.id,
            },
        }
