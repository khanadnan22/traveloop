# -*- coding: utf-8 -*-
from odoo import api, fields, models


class TravelCity(models.Model):
    _name = 'travel.city'
    _description = 'Travel City'
    _order = 'name'
    _inherit = ['mail.thread']

    name = fields.Char(string='City Name', required=True, tracking=True)
    country_id = fields.Many2one('res.country', string='Country', required=True)
    country_code = fields.Char(related='country_id.code', store=True)
    description = fields.Html(string='Description')
    image = fields.Image(string='City Image', max_width=1920, max_height=1080)
    cost_index = fields.Selection([
        ('1', '$ Budget'),
        ('2', '$$ Moderate'),
        ('3', '$$$ Expensive'),
        ('4', '$$$$ Luxury'),
    ], string='Cost Index', default='2', tracking=True)
    avg_daily_cost = fields.Float(string='Avg. Daily Cost (USD)', help='Average daily cost for a traveler in USD')
    popularity = fields.Integer(string='Popularity Score', default=0, help='Higher is more popular')
    latitude = fields.Float(string='Latitude', digits=(10, 7))
    longitude = fields.Float(string='Longitude', digits=(10, 7))
    timezone = fields.Char(string='Timezone')
    language = fields.Char(string='Local Language')
    currency_name = fields.Char(string='Local Currency')
    best_time_to_visit = fields.Char(string='Best Time to Visit')
    active = fields.Boolean(default=True)


    stop_count = fields.Integer(compute='_compute_stop_count', string='Times Visited')
    activity_count = fields.Integer(compute='_compute_activity_count', string='Activities Available')

    _sql_constraints = [
        ('name_country_unique', 'UNIQUE(name, country_id)', 'This city already exists for the selected country!')
    ]

    def _compute_stop_count(self):
        for city in self:
            city.stop_count = self.env['travel.stop'].search_count([('city_id', '=', city.id)])

    def _compute_activity_count(self):
        for city in self:
            city.activity_count = self.env['travel.activity'].search_count([('city_id', '=', city.id)])

    def action_view_activities(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Activities in {self.name}',
            'res_model': 'travel.activity',
            'view_mode': 'list,form',
            'domain': [('city_id', '=', self.id)],
            'context': {'default_city_id': self.id},
        }
