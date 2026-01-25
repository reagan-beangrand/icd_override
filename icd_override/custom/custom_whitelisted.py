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

