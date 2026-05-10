# -*- coding: utf-8 -*-
import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import random

class TravelGeneratorWizard(models.TransientModel):
    _name = 'travel.generator.wizard'
    _description = 'Magic AI Trip Generator'

    destination_vibe = fields.Selection([
        ('europe', 'European Adventure'),
        ('asia', 'Asian Discovery'),
        ('beach', 'Tropical Escape'),
        ('mixed', 'Surprise Me!'),
    ], string='Vibe', default='mixed', required=True)
    
    budget_level = fields.Selection([
        ('1', '$ Budget'),
        ('2', '$$ Moderate'),
        ('3', '$$$ Expensive'),
        ('4', '$$$$ Luxury'),
    ], string='Budget Level', default='2', required=True)
    
    duration = fields.Integer(string='Duration (Days)', default=7, required=True)
    start_date = fields.Date(string='Start Date', default=fields.Date.context_today, required=True)
    
    def action_generate_trip(self):
        self.ensure_one()
        
        # 1. Select cities based on vibe
        domain = [('cost_index', 'in', [self.budget_level, str(max(1, int(self.budget_level)-1)), str(min(4, int(self.budget_level)+1))])]
        all_cities = self.env['travel.city'].search(domain)
        
        if not all_cities:
            # Fallback if no exact budget match
            all_cities = self.env['travel.city'].search([])
            
        if not all_cities:
            raise UserError(_("No cities found in database. Please load demo data."))
            
        # Filter by "vibe" (using country codes or random for this hackathon demo)
        europe_codes = ['FR', 'IT', 'GB', 'DE', 'ES', 'NL']
        asia_codes = ['JP', 'TH', 'IN', 'VN', 'CN']
        beach_codes = ['ID', 'TH', 'MX', 'BR', 'MV']
        
        filtered_cities = all_cities
        if self.destination_vibe == 'europe':
            filtered_cities = all_cities.filtered(lambda c: c.country_id.code in europe_codes)
        elif self.destination_vibe == 'asia':
            filtered_cities = all_cities.filtered(lambda c: c.country_id.code in asia_codes)
        elif self.destination_vibe == 'beach':
            filtered_cities = all_cities.filtered(lambda c: c.country_id.code in beach_codes)
            
        if not filtered_cities:
            filtered_cities = all_cities
            
        # Select 2-3 cities for the trip
        num_stops = min(max(1, self.duration // 3), len(filtered_cities))
        selected_cities = random.sample(list(filtered_cities), num_stops)
        
        # 2. Create the Trip
        trip_name = f"Magic {dict(self._fields['destination_vibe'].selection).get(self.destination_vibe)} ({self.duration} Days)"
        trip = self.env['travel.trip'].create({
            'name': trip_name,
            'date_start': self.start_date,
            'date_end': self.start_date + datetime.timedelta(days=self.duration),
            'description': f"<p>Auto-generated AI itinerary for {self.duration} days. Budget level: {self.budget_level}/4.</p>",
            'state': 'draft',
        })
        
        # 3. Create Stops
        current_date = self.start_date
        days_per_stop = self.duration // num_stops
        
        for i, city in enumerate(selected_cities):
            is_last = (i == len(selected_cities) - 1)
            stop_duration = days_per_stop if not is_last else (self.duration - (days_per_stop * i))
            departure = current_date + datetime.timedelta(days=stop_duration)
            
            stop = self.env['travel.stop'].create({
                'trip_id': trip.id,
                'sequence': i * 10,
                'city_id': city.id,
                'arrival_date': current_date,
                'departure_date': departure,
                'transport_mode': 'flight' if i == 0 else 'train',
                'transport_cost': random.randint(50, 300) * int(self.budget_level),
                'accommodation': 'AI Suggested Hotel',
                'accommodation_cost': random.randint(40, 200) * int(self.budget_level),
            })
            
            # Add some activities to the stop
            available_activities = self.env['travel.activity'].search([('city_id', '=', city.id)])
            if not available_activities:
                # If no specific activities for this city, create generic ones
                activities_to_create = [
                    {'name': f'City Tour in {city.name}', 'activity_type': 'sightseeing', 'cost': 50},
                    {'name': f'Local Dinner', 'activity_type': 'food', 'cost': 40},
                ]
                for act in activities_to_create:
                    self.env['travel.activity'].create({
                        'stop_id': stop.id,
                        'name': act['name'],
                        'activity_type': act['activity_type'],
                        'date': current_date + datetime.timedelta(days=1),
                        'cost': act['cost'] * int(self.budget_level),
                    })
            else:
                # Use existing activities
                num_activities = min(2, len(available_activities))
                for act in random.sample(list(available_activities), num_activities):
                    act.copy({'stop_id': stop.id, 'date': current_date + datetime.timedelta(days=1)})
                    
            current_date = departure
            
        # 4. Generate Checklist
        trip.action_generate_packing_list()
        
        # Return action to open the newly created trip
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'travel.trip',
            'res_id': trip.id,
            'view_mode': 'form',
            'target': 'current',
        }
