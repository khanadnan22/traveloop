# -*- coding: utf-8 -*-
from odoo import api, fields, models


class TravelChecklistItem(models.Model):
    _name = 'travel.checklist.item'
    _description = 'Packing Checklist Item'
    _order = 'category, sequence, name'

    name = fields.Char(string='Item', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    trip_id = fields.Many2one('travel.trip', string='Trip', required=True, ondelete='cascade')
    category = fields.Selection([
        ('clothing', 'Clothing'),
        ('toiletries', 'Toiletries'),
        ('electronics', 'Electronics'),
        ('documents', 'Documents'),
        ('medicine', 'Medicine'),
        ('accessories', 'Accessories'),
        ('food', 'Snacks & Food'),
        ('other', 'Other'),
    ], string='Category', default='other', required=True)
    is_packed = fields.Boolean(string='Packed', default=False)
    quantity = fields.Integer(string='Quantity', default=1)
    notes = fields.Text(string='Notes')

    def action_toggle_packed(self):
        for item in self:
            item.is_packed = not item.is_packed
