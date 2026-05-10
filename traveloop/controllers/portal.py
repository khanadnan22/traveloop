# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal


class TraveloopPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'trip_count' in counters:
            values['trip_count'] = request.env['travel.trip'].search_count(
                [('user_id', '=', request.env.user.id)]
            )
        return values

    @http.route('/my/trips', type='http', auth='user', website=True)
    def portal_my_trips(self, **kw):
        trips = request.env['travel.trip'].search([
            ('user_id', '=', request.env.user.id)
        ], order='date_start desc')
        values = {
            'trips': trips,
            'page_name': 'trips',
        }
        return request.render('traveloop.portal_my_trips', values)

    @http.route('/my/trips/<int:trip_id>', type='http', auth='user', website=True)
    def portal_my_trip_detail(self, trip_id, **kw):
        trip = request.env['travel.trip'].browse(trip_id)
        if trip.user_id != request.env.user:
            return request.redirect('/my/trips')
        values = {
            'trip': trip,
            'page_name': 'trip_detail',
        }
        return request.render('traveloop.portal_my_trip_detail', values)

    @http.route('/travel/shared/<string:token>', type='http', auth='public', website=True)
    def shared_trip_view(self, token, **kw):
        trip = request.env['travel.trip'].sudo().search([
            ('share_token', '=', token),
            ('is_shared', '=', True),
        ], limit=1)
        if not trip:
            return request.not_found()
        values = {
            'trip': trip,
        }
        return request.render('traveloop.shared_trip_view', values)
