# -*- coding: utf-8 -*-
from odoo import api, fields, models


class TravelExpense(models.Model):
    _name = 'travel.expense'
    _description = 'Travel Expense'
    _order = 'date desc, id desc'

    name = fields.Char(string='Description', required=True)
    trip_id = fields.Many2one('travel.trip', string='Trip', required=True, ondelete='cascade')
    stop_id = fields.Many2one('travel.stop', string='Related Stop',
                              domain="[('trip_id', '=', trip_id)]")
    date = fields.Date(string='Date', default=fields.Date.context_today)
    currency_id = fields.Many2one(related='trip_id.currency_id')
    amount = fields.Monetary(string='Amount', currency_field='currency_id', required=True)
    category = fields.Selection([
        ('transport', 'Transport'),
        ('accommodation', 'Accommodation'),
        ('food', 'Food & Dining'),
        ('activity', 'Activities'),
        ('shopping', 'Shopping'),
        ('communication', 'Communication'),
        ('insurance', 'Insurance'),
        ('visa', 'Visa & Fees'),
        ('other', 'Other'),
    ], string='Category', default='other', required=True)
    payment_method = fields.Selection([
        ('cash', 'Cash'),
        ('card', 'Credit/Debit Card'),
        ('online', 'Online Payment'),
        ('other', 'Other'),
    ], string='Payment Method', default='card')
    receipt = fields.Binary(string='Receipt')
    notes = fields.Text(string='Notes')
