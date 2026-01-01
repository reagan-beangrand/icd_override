import frappe
from frappe.utils import getdate, add_days, nowdate

@frappe.whitelist()
def get_daily_truck_entries_exits(from_date: str | None = None, to_date: str | None = None):
	"""Return daily counts of truck entries and exits.

	Assumptions:
	- Entries are driven by `Container Reception.received_date`.
	- Exits are driven by `Gatepass.creation` date (document creation time) since there is no explicit date field.

	Returns 2 datasets suitable for a time-series chart.
	"""

	# Resolve date range
	if not to_date:
		to_date = nowdate()
	if not from_date:
		from_date = add_days(to_date, -29)

	from_date = getdate(from_date)
	to_date = getdate(to_date)

	# Entries per day from Container Reception
	entries = frappe.db.sql(
		"""
			select received_date as d, count(*) as c
			from `tabContainer Reception`
			where received_date between %(from_date)s and %(to_date)s
			group by received_date
		""",
		{"from_date": from_date, "to_date": to_date},
		as_dict=True,
	)
	entries_map = {getdate(r["d"]): r["c"] for r in entries if r["d"]}

	# Exits per day from Gatepass (using creation date)
	exits = frappe.db.sql(
		"""
			select date(creation) as d, count(*) as c
			from `tabGate Pass`
			where docstatus=1 and date(creation) between %(from_date)s and %(to_date)s
			group by date(creation)
		""",
		{"from_date": from_date, "to_date": to_date},
		as_dict=True,
	)
	exits_map = {getdate(r["d"]): r["c"] for r in exits if r["d"]}

	# Build continuous date labels
	labels: list[str] = []
	entry_values: list[int] = []
	exit_values: list[int] = []

	cur = from_date
	while cur <= to_date:
		labels.append(cur.isoformat())
		entry_values.append(int(entries_map.get(cur, 0)))
		exit_values.append(int(exits_map.get(cur, 0)))
		cur = add_days(cur, 1)

	return {
		"labels": labels,
		"datasets": [
			{"name": "Entries", "values": entry_values},
			{"name": "Exits", "values": exit_values},
		],
	}