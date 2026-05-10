# -*- coding: utf-8 -*-
{
    'name': 'Traveloop - Personalized Travel Planning',
    'version': '19.0.1.0.0',
    'category': 'Services/Travel',
    'summary': 'Plan, organize and share personalized multi-city travel itineraries',
    'description': """
Traveloop - Travel Planning

A platform to manage travel plans:
* Create multi-city itineraries
* Assign dates, activities, and budgets
* Discover activities and destinations
* Cost tracking and calendar views
* Share plans
* Packing checklists
* Trip notes and journals

Features:
- Dashboard with upcoming trips
- Itinerary Builder
- City and Activity discovery
- Budget tracking
- Packing checklist
- Trip notes
- Shareable itinerary views
- Analytics dashboard
    """,
    'author': 'Traveloop Team',
    'website': 'https://traveloop.app',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
        'portal',
        'web',
        'web_gantt',
    ],
    'data': [
        # Security
        'security/traveloop_security.xml',
        'security/ir.model.access.csv',
        # Data
        'data/traveloop_data.xml',
        # Wizard
        'wizard/travel_generator_views.xml',
        # Views
        'views/travel_trip_views.xml',
        'views/travel_stop_views.xml',
        'views/travel_activity_views.xml',
        'views/travel_city_views.xml',
        'views/travel_checklist_views.xml',
        'views/travel_note_views.xml',
        'views/travel_expense_views.xml',

        # Menus
        'views/traveloop_menus.xml',
        # Portal
        'views/portal_templates.xml',
        'data/traveloop_demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'traveloop/static/src/scss/traveloop_backend.scss',
            'traveloop/static/src/js/traveloop_dashboard.js',
            'traveloop/static/src/xml/traveloop_dashboard.xml',
        ],
    },
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'sequence': 1,
}
