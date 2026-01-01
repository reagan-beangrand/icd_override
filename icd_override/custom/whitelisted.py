import frappe
from frappe.core.doctype.access_log.access_log import make_access_log

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