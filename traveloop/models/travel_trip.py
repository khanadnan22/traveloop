# -*- coding: utf-8 -*-
import uuid
from datetime import timedelta

from odoo import api, fields, models, _
# pyrefly: ignore [missing-import]
from odoo.exceptions import ValidationError


class TravelTrip(models.Model):
    _name = 'travel.trip'
    _description = 'Travel Trip'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _order = 'date_start desc, id desc'

    name = fields.Char(string='Trip Name', required=True, tracking=True)
    description = fields.Html(string='Description')
    cover_image = fields.Image(string='Cover Photo', max_width=1920, max_height=1080)
    user_id = fields.Many2one('res.users', string='Traveler', default=lambda self: self.env.user,
                              required=True, tracking=True)
    partner_id = fields.Many2one('res.partner', related='user_id.partner_id', store=True)


    date_start = fields.Date(string='Start Date', required=True, tracking=True)
    date_end = fields.Date(string='End Date', required=True, tracking=True)
    duration_days = fields.Integer(string='Duration (Days)', compute='_compute_duration_days', store=True)


    state = fields.Selection([
        ('draft', 'Planning'),
        ('confirmed', 'Confirmed'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True, required=True)
    color = fields.Integer(string='Color Index')


    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.company.currency_id)
    total_budget = fields.Monetary(string='Total Budget', currency_field='currency_id', tracking=True)
    total_estimated_cost = fields.Monetary(string='Estimated Cost', currency_field='currency_id',
                                           compute='_compute_costs', store=True)
    budget_remaining = fields.Monetary(string='Budget Remaining', currency_field='currency_id',
                                       compute='_compute_costs', store=True)
    is_over_budget = fields.Boolean(string='Over Budget', compute='_compute_costs', store=True)


    stop_ids = fields.One2many('travel.stop', 'trip_id', string='Stops')
    checklist_ids = fields.One2many('travel.checklist.item', 'trip_id', string='Packing Checklist')
    note_ids = fields.One2many('travel.note', 'trip_id', string='Trip Notes')
    expense_ids = fields.One2many('travel.expense', 'trip_id', string='Expenses')


    stop_count = fields.Integer(compute='_compute_counts', string='Stops')
    activity_count = fields.Integer(compute='_compute_counts', string='Activities')
    checklist_count = fields.Integer(compute='_compute_counts', string='Checklist Items')
    note_count = fields.Integer(compute='_compute_counts', string='Notes')
    checklist_progress = fields.Float(compute='_compute_checklist_progress', string='Packing Progress')


    share_token = fields.Char(string='Share Token', copy=False, readonly=True)
    is_shared = fields.Boolean(string='Publicly Shared', default=False, tracking=True)

    _sql_constraints = [
        ('date_check', 'CHECK(date_end >= date_start)', 'End date must be after start date!'),
    ]

    @api.depends('date_start', 'date_end')
    def _compute_duration_days(self):
        for trip in self:
            if trip.date_start and trip.date_end:
                trip.duration_days = (trip.date_end - trip.date_start).days + 1
            else:
                trip.duration_days = 0

    @api.depends('stop_ids.estimated_cost', 'expense_ids.amount', 'total_budget')
    def _compute_costs(self):
        for trip in self:
            trip.total_estimated_cost = sum(trip.stop_ids.mapped('estimated_cost'))
            if trip.expense_ids:
                trip.total_estimated_cost += sum(trip.expense_ids.mapped('amount'))
            trip.budget_remaining = trip.total_budget - trip.total_estimated_cost
            trip.is_over_budget = trip.total_estimated_cost > trip.total_budget if trip.total_budget else False

    def _compute_counts(self):
        for trip in self:
            trip.stop_count = len(trip.stop_ids)
            trip.activity_count = sum(len(stop.activity_ids) for stop in trip.stop_ids)
            trip.checklist_count = len(trip.checklist_ids)
            trip.note_count = len(trip.note_ids)

    @api.depends('checklist_ids.is_packed')
    def _compute_checklist_progress(self):
        for trip in self:
            total = len(trip.checklist_ids)
            if total:
                packed = len(trip.checklist_ids.filtered('is_packed'))
                trip.checklist_progress = (packed / total) * 100
            else:
                trip.checklist_progress = 0

    @api.constrains('date_start', 'date_end')
    def _check_dates(self):
        for trip in self:
            if trip.date_start and trip.date_end and trip.date_end < trip.date_start:
                raise ValidationError(_('End date cannot be before start date.'))

    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_start(self):
        self.write({'state': 'ongoing'})

    def action_complete(self):
        self.write({'state': 'completed'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_draft(self):
        self.write({'state': 'draft'})

    def action_share(self):
        """Generate a share token and mark as shared"""
        for trip in self:
            if not trip.share_token:
                trip.share_token = str(uuid.uuid4())
            trip.is_shared = True
        return {
            'type': 'ir.actions.act_url',
            'url': f'/travel/shared/{self.share_token}',
            'target': 'new',
        }

    def action_generate_packing_list(self):
        """Auto-generate packing list based on duration and activities"""
        for trip in self:
            days = trip.duration_days or 1
            items_to_create = []

            # Base items for any trip
            items_to_create.extend([
                {'name': 'Passport/ID', 'category': 'documents', 'quantity': 1},
                {'name': 'Phone Charger', 'category': 'electronics', 'quantity': 1},
                {'name': 'Toothbrush & Paste', 'category': 'toiletries', 'quantity': 1},
                {'name': 'Deodorant', 'category': 'toiletries', 'quantity': 1},
                {'name': 'Underwear', 'category': 'clothing', 'quantity': days + 1},
                {'name': 'Socks', 'category': 'clothing', 'quantity': days + 1},
                {'name': 'T-Shirts', 'category': 'clothing', 'quantity': days},
            ])

            # Activity-specific items
            activity_types = set(trip.stop_ids.mapped('activity_ids.activity_type'))
            if 'beach' in activity_types:
                items_to_create.extend([
                    {'name': 'Swimsuit', 'category': 'clothing', 'quantity': 2},
                    {'name': 'Sunscreen', 'category': 'toiletries', 'quantity': 1},
                    {'name': 'Sunglasses', 'category': 'accessories', 'quantity': 1},
                ])
            if 'nature' in activity_types or 'adventure' in activity_types:
                items_to_create.extend([
                    {'name': 'Hiking Boots', 'category': 'clothing', 'quantity': 1},
                    {'name': 'Bug Repellent', 'category': 'toiletries', 'quantity': 1},
                    {'name': 'Water Bottle', 'category': 'accessories', 'quantity': 1},
                ])

            # Filter out existing items
            existing_names = set(trip.checklist_ids.mapped('name'))
            for item in items_to_create:
                if item['name'] not in existing_names:
                    item['trip_id'] = trip.id
                    self.env['travel.checklist.item'].create(item)


    def action_unshare(self):
        self.write({'is_shared': False})

    def action_copy_trip(self):
        """Create a copy of this trip for the current user"""
        self.ensure_one()
        new_trip = self.copy({
            'name': f'{self.name} (Copy)',
            'user_id': self.env.user.id,
            'state': 'draft',
            'share_token': False,
            'is_shared': False,
        })
        return {
            'type': 'ir.actions.act_window',
            'name': _('Copied Trip'),
            'res_model': 'travel.trip',
            'view_mode': 'form',
            'res_id': new_trip.id,
        }

    def action_view_stops(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Trip Stops'),
            'res_model': 'travel.stop',
            'view_mode': 'list,form',
            'domain': [('trip_id', '=', self.id)],
            'context': {'default_trip_id': self.id},
        }

    def action_view_checklist(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Packing Checklist'),
            'res_model': 'travel.checklist.item',
            'view_mode': 'list,form',
            'domain': [('trip_id', '=', self.id)],
            'context': {'default_trip_id': self.id},
        }

    def action_view_notes(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Trip Notes'),
            'res_model': 'travel.note',
            'view_mode': 'list,form',
            'domain': [('trip_id', '=', self.id)],
            'context': {'default_trip_id': self.id},
        }

    def action_view_expenses(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Trip Expenses'),
            'res_model': 'travel.expense',
            'view_mode': 'list,form,pivot,graph',
            'domain': [('trip_id', '=', self.id)],
            'context': {'default_trip_id': self.id},
        }

    def _compute_access_url(self):
        super()._compute_access_url()
        for trip in self:
            trip.access_url = f'/my/trips/{trip.id}'
