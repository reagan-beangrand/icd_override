frappe.provide("frappe.dashboards.chart_sources");

frappe.dashboards.chart_sources["Containers InYard By Status"] = {
	method: "icd_override.custom.dashboard_chart_source.containers_inyard_by_status.get_containers_in_yard_by_status",
	filters: [],
};