import frappe
from icd_tz.icd_tz.doctype.container_inspection.container_inspection import ContainerInspection


class CustomContainerInspection(ContainerInspection):
    @frappe.whitelist()
    def get_custom_verification_services(self, caller=None):
        if caller == "Front End" and isinstance(self, str):
            self = frappe.parse_json(self)
        
        if not self.get("in_yard_container_booking"):
            return
        
        has_custom_verification_charges = frappe.db.get_value(
			"In Yard Container Booking",
            self.get("in_yard_container_booking"),
            "has_custom_verification_charges"
		)

        if has_custom_verification_charges != "Yes":
            return
        
        verification_item = ""
        settings_doc = frappe.get_cached_doc("ICD TZ Settings")
        container_doc = frappe.get_doc("Container", self.container_id)#reagan
        is_dg = True if container_doc.custom_dangerous_goods==1 else False
        for row in settings_doc.get("service_types"):
            #if container_doc.custom_dangerous_goods==0:
            if not is_dg and row.service_type == "Verification":
                    if "2" in str(row.size)[0] and "2" in str(self.container_size)[0]:
                        verification_item = row.service_name
                        break

                    elif "4" in str(row.size)[0] and "4" in str(self.container_size)[0]:
                        verification_item = row.service_name
                        break
                    else:
                        continue
            elif is_dg and row.service_type == "DG-Verification":
                if "2" in str(row.size)[0] and "2" in str(self.container_size)[0]:
                    verification_item = row.service_name
                    break

                elif "4" in str(row.size)[0] and "4" in str(self.container_size)[0]:
                    verification_item = row.service_name
                    break
                else:
                    continue

        if not verification_item:
            frappe.throw("Verification Pricing Criteria is not set in ICD TZ Settings, Please set it to continue")
        
        service_names = [row.get("service") for row in self.get("services")]
        if verification_item not in service_names:
            if caller == "Front End":
                return verification_item
            else:
                self.append("services", {
                    "service": verification_item
                })