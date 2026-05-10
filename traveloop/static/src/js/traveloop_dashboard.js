/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

class TraveloopDashboard extends Component {
    static template = "traveloop.Dashboard";

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = useState({
            trips: [],
            stats: {
                total_trips: 0,
                upcoming_trips: 0,
                total_stops: 0,
                total_budget: 0,
            },
            popularCities: [],
            loading: true,
        });

        onWillStart(async () => {
            await this.loadDashboardData();
        });
    }

    async loadDashboardData() {
        try {
            // Load trips
            const trips = await this.orm.searchRead(
                "travel.trip",
                [],
                ["name", "date_start", "date_end", "state", "stop_count",
                 "total_budget", "total_estimated_cost", "duration_days", "cover_image"],
                { order: "date_start desc", limit: 6 }
            );

            // Load stats
            const allTrips = await this.orm.searchRead(
                "travel.trip",
                [],
                ["total_budget", "state", "stop_count", "note_count"],
            );

            const upcomingTrips = allTrips.filter(t => t.state !== 'completed' && t.state !== 'cancelled');
            const completedTrips = allTrips.filter(t => t.state === 'completed');

            // Load popular cities
            const cities = await this.orm.searchRead(
                "travel.city",
                [],
                ["name", "country_id", "cost_index", "avg_daily_cost", "popularity", "image"],
                { order: "popularity desc", limit: 6 }
            );

            this.state.trips = trips;
            this.state.stats = {
                total_trips: allTrips.length,
                upcoming_trips: upcomingTrips.length,
                completed_trips: completedTrips.length,
                total_notes: allTrips.reduce((sum, t) => sum + (t.note_count || 0), 0),
                total_stops: allTrips.reduce((sum, t) => sum + t.stop_count, 0),
                total_budget: allTrips.reduce((sum, t) => sum + t.total_budget, 0),
            };
            this.state.popularCities = cities;
            this.state.loading = false;
        } catch (error) {
            console.error("Dashboard load error:", error);
            this.state.loading = false;
        }
    }

    openTrips() {
        this.action.doAction("traveloop.action_travel_trip");
    }

    createTrip() {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "New Trip",
            res_model: "travel.trip",
            view_mode: "form",
            views: [[false, "form"]],
            target: "current",
        });
    }

    openTrip(tripId) {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Trip",
            res_model: "travel.trip",
            view_mode: "form",
            res_id: tripId,
            views: [[false, "form"]],
            target: "current",
        });
    }

    exploreCities() {
        this.action.doAction("traveloop.action_travel_city");
    }

    openExpenses() {
        this.action.doAction("traveloop.action_travel_expense");
    }

    openChecklist() {
        this.action.doAction("traveloop.action_travel_checklist");
    }

    getStateColor(state) {
        const colors = {
            draft: '#6c757d',
            confirmed: '#0d6efd',
            ongoing: '#198754',
            completed: '#20c997',
            cancelled: '#dc3545',
        };
        return colors[state] || '#6c757d';
    }

    getStateLabel(state) {
        const labels = {
            draft: 'Planning',
            confirmed: 'Confirmed',
            ongoing: 'Ongoing',
            completed: 'Completed',
            cancelled: 'Cancelled',
        };
        return labels[state] || state;
    }

    formatCurrency(amount) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 0,
        }).format(amount);
    }
}

registry.category("actions").add("traveloop_dashboard", TraveloopDashboard);
