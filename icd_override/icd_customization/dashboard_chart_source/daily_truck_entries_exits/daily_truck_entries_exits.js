frappe.provide("frappe.dashboards.chart_sources");

frappe.dashboards.chart_sources["Daily Truck Entries Exits"] = {
	method: "icd_override.custom.dashboard_chart_source.daily_truck_entries_exits.get_daily_truck_entries_exits",
	filters: [
		{ fieldname: "from_date", label: __("From Date"), fieldtype: "Date" },
		{ fieldname: "to_date", label: __("To Date"), fieldtype: "Date" },
	],
};

