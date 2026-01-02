import frappe
from icd_tz.icd_tz.doctype.gate_pass.gate_pass import GatePass
from frappe.utils import (
    get_fullname,
	nowdate,
	nowtime,
	now_datetime,
	get_url_to_form,
	add_to_date,
	get_datetime,
)
#Commented  workflow state
class CustomGatePass(GatePass):
    def on_update_after_submit(self):
        #frappe.msgprint("ICD_OVERRIDE - Custom on_update_after_submit called.")
        self.validate_pending_payments()
        #if self.workflow_state == "Gate Out Confirmed":
        self.set_gate_out_date()
        self.update_container_status("Delivered")

    """Validate the pending payments for the Gate Pass"""
    def validate_pending_payments(self):
        if self.is_empty_container == 1:
            return

        service_msg = ""
        service_msg += self.validate_container_charges()
        service_msg += self.validate_in_yard_booking()
        service_msg += self.validate_reception_charges()
        service_msg += self.validate_inspection_charges()

        if service_msg:
            msg = "<h4 class='text-center'>Pending Payments:</h4><hr>Payment is pending for the following services <ul> " + service_msg + " </ul>"

            #if self.workflow_state in ["Approved", "Gate Out Confirmed"]:
             #   frappe.throw(str(msg))
            #else:
            frappe.msgprint(str(msg))

    """Validate the storage payments for the Gate Pass"""
    def validate_container_charges(self):
        msg=""
        container_info = frappe.db.get_value(
			"Container",
			self.container_id,
			["has_removal_charges", "r_sales_invoice", "has_corridor_levy_charges", "c_sales_invoice", "days_to_be_billed"],
			as_dict=True
		)
        if container_info.days_to_be_billed > 0:
            msg += f"<li>Storage Charges:  <b>{container_info.days_to_be_billed} Days</b></li>"
        
        if container_info.has_removal_charges == "Yes" and not container_info.r_sales_invoice:
            msg += "<li>Removal Charges</li>"
        if container_info.has_corridor_levy_charges == "Yes" and not container_info.c_sales_invoice:
            msg += "<li>Corridor Levy Charges</li>"
        return msg
    
    """Validate the In Yard Container Booking for the Gate Pass"""
    def validate_in_yard_booking(self):
        msg = ""
        booking_info = frappe.db.get_all(
			"In Yard Container Booking",
			{
				"container_id": self.container_id,
				"docstatus": ["!=", 2],  # Exclude cancelled bookings
			},
			["has_stripping_charges", "s_sales_invoice", "has_custom_verification_charges", "cv_sales_invoice"],
		)
        cargo_type = frappe.get_cached_value(
			"Container",
			self.container_id,
			"cargo_type"
		)
        if (
			len(booking_info) == 0 and
			cargo_type != "Transit" and # Transit containers are not required to have booking
			self.action_for_missing_booking == 'Stop'
		):
            frappe.throw(
				f"No Booking found for container: <b>{self.container_no}</b>, Cargo Type: <b>{cargo_type}</b><br>If you want to proceed, Please inform relevant person to Approve this Gate Pass"
			)

        for row in booking_info:
            if row.has_stripping_charges == "Yes" and not row.s_sales_invoice:
                msg += "<li>Stripping Charges</li>"
            if row.has_custom_verification_charges == "Yes" and not row.cv_sales_invoice:
                msg += "<li>Custom Verification Charges</li>"
        
        return msg
    
    """Validate the Reception Charges for the Gate Pass"""
    def validate_reception_charges(self):
        msg = ""
        container_reception = frappe.db.get_value(
			"Container",
			self.container_id,
			"container_reception"
		)
        if not container_reception:
            return msg
        reception_info = frappe.db.get_value(
			"Container Reception",
			container_reception,
			["cargo_type", "has_transport_charges", "t_sales_invoice", "has_shore_handling_charges", "s_sales_invoice"],
			as_dict=True
		)
        if (
			reception_info.has_transport_charges == "Yes"
			and not reception_info.t_sales_invoice
			# Transport is not mandatory service for Transit container
			and reception_info.cargo_type != "Transit"
		):
            msg += "<li>Transport Charges</li>"
        if reception_info.has_shore_handling_charges == "Yes" and not reception_info.s_sales_invoice:
            msg += "<li>Shore Handling Charges</li>"
        return msg
    
    """Validate the Inspection Charges for the Gate Pass"""
    def validate_inspection_charges(self):
        msg = ""
        inspection_info = frappe.db.get_all(
			"Container Inspection",
			{"container_id": self.container_id},
			pluck="name"
		)
        if len(inspection_info) == 0:
            return msg
        for inspection in inspection_info:
            inspection_doc = frappe.get_doc("Container Inspection", inspection)
            for d in inspection_doc.get("services"):
                if "off" in str(d.get("service")).lower() and not d.get("sales_invoice"):
                    msg += f"<li>{d.get('service')}</li>"
                if "status" in str(d.get("service")).lower() and not d.get("sales_invoice"):
                    msg += f"<li>{d.get('service')}</li>"
        return msg
    
    """Stamp the gate out datetime once the workflow is confirmed."""
    def set_gate_out_date(self):
        if self.gate_out_date:
            return
        gate_out_datetime = now_datetime()
        self.db_set("gate_out_date", gate_out_datetime)
    
    """Update the Container Status when the Gate Pass is submitted."""
    def update_container_status(self, status="Delivered"):
        if not self.container_id:
            return
              
        container_doc = frappe.get_cached_doc("Container", self.container_id)
        container_doc.status = status
        container_doc.save(ignore_permissions=True)
        container_doc.reload()
    