import frappe


@frappe.whitelist()
def get_containers_in_yard_by_status():
	"""Return count of containers grouped by current status.

	Uses `Container Details.status` values: e.g., "In Yard", "In Inspection", "At Gatepass".
	Returns data formatted for Frappe dashboard charts.
	"""

	rows = frappe.db.sql(
		"""
			select coalesce(status, 'Unknown') as status, count(*) as count
			from `tabContainer`
			group by tabContainer.status
			order by count desc
		""",
		as_dict=True,
	)

	labels = [r["status"] for r in rows]
	values = [r["count"] for r in rows]

	return {
		"labels": labels,
		"datasets": [{"name": "Containers", "values": values}],
	}