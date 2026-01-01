import frappe
from frappe.utils import add_days, nowdate

@frappe.whitelist()
def get_top_customers_by_revenue(from_date: str | None = None, to_date: str | None = None, limit: int = 10):
	"""Return top customers by revenue from Sales Invoices.

	- Considers submitted invoices (`docstatus = 1`).
	- Uses `posting_date` for date filtering.
	- Sums `base_grand_total` for stable currency comparison.
	"""

	if not to_date:
		to_date = nowdate()
	if not from_date:
		from_date = add_days(to_date, -89)

	rows = frappe.db.sql(
		"""
			select
				coalesce(customer_name, customer) as customer,
				sum(base_grand_total) as revenue
			from `tabSales Invoice`
			where docstatus = 1
				and posting_date between %(from_date)s and %(to_date)s
			group by coalesce(customer_name, customer)
			order by revenue desc
			limit %(limit)s
		""",
		{"from_date": from_date, "to_date": to_date, "limit": int(limit)},
		as_dict=True,
	)

	labels = [r["customer"] for r in rows]
	values = [float(r["revenue"]) for r in rows]

	return {
		"labels": labels,
		"datasets": [{"name": "Revenue", "values": values}],
	}