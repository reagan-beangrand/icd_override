import frappe
from frappe.query_builder import DocType
from frappe.core.doctype.access_log.access_log import make_access_log


mf = DocType("Manifest")
mb = DocType("Master BL")
cd = DocType("Containers Detail")

@frappe.whitelist()
def get_manifest_details(manifest, container_no=None):
	"""Get details of a manifest and container information"""
	
	query = (
        frappe.qb.from_(mf)
		.inner_join(cd)
		.on(mf.name == cd.parent)
        .inner_join(mb)
        .on(cd.m_bl_no == mb.m_bl_no)
        .select(
			mf.mrn,
			mf.vessel_name,
			mf.tpa_uid,
			mf.voyage_no,
			mf.arrival_date,
			mf.call_sign,
			mf.company,
            cd.container_no,
            cd.m_bl_no,
            cd.container_size,
			cd.freight_indicator,
            mb.cargo_classification.as_("cargo_type")
        )
        .where(
			(mf.name == manifest)
			& (cd.has_order == 0)
			& (cd.parent == manifest)
			& (mb.parent == manifest)
		)
    )

	if container_no:
		query = query.where(			
			(cd.container_no == container_no)
		)
	
	details = query.run(as_dict=True)
	
	return details

@frappe.whitelist()
def get_container_details(manifest, container_no):	
	"""Get the details of a container based on the container no and manifest"""
	#frappe.msgprint(f"Inside override get_container_details with manifest: {manifest} and container_no: {container_no}")
	container = frappe.db.get_all(
		"Containers Detail",
		filters={"parent": manifest, "container_no": container_no},
		fields=["*"]
	)

	if len(container) > 0:
		container_row = container[0]
		abbr_for_destination = frappe.db.get_value(
			"Master BL",
			{"parent": manifest, "m_bl_no": container_row.m_bl_no},
			"place_of_destination"
		)
		container_row["abbr_for_destination"] = abbr_for_destination

		country_code = str(abbr_for_destination)[:2]
		country_of_destination = frappe.get_cached_value(
			"Country", {"code": country_code.lower()}, "name"
		)
		container_row["country_of_destination"] = country_of_destination

		place_of_destination = ""
		if country_code == "TZ":
			place_of_destination = "Local"
		elif country_code == "CD":
			place_of_destination = "DRC"
		elif country_code == "UG":
			place_of_destination = "Uganda"
		else:
			place_of_destination = "Transit"#"Other"

		container_row["place_of_destination"] = place_of_destination

		return container_row
#sample to test whitelisting override - not used in production
@frappe.whitelist()
def download_vcard(contact: str):
	"""Download vCard for the contact"""
	print("Inside icd_override.whitelist() download_vcards")
	contact = frappe.get_doc("Contact", contact)
	contact.check_permission()

	vcard = contact.get_vcard()
	make_access_log(doctype="Contact", document=contact.name, file_type="vcf")

	frappe.response["filename"] = f"{contact.name}.vcf"
	frappe.response["filecontent"] = vcard.serialize().encode("utf-8")
	frappe.response["type"] = "binary"

