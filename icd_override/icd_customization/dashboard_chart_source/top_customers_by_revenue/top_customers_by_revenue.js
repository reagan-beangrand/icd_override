frappe.provide("frappe.dashboards.chart_sources");

frappe.dashboards.chart_sources["Top Customers By Revenue"] = {
	method: "icd_override.custom.dashboard_chart_source.top_customers_by_revenue.get_top_customers_by_revenue",
	filters: [
		{ fieldname: "from_date", label: __("From Date"), fieldtype: "Date" },
		{ fieldname: "to_date", label: __("To Date"), fieldtype: "Date" },
		{ fieldname: "limit", label: __("Limit"), fieldtype: "Int", default: 10 },
	],
};