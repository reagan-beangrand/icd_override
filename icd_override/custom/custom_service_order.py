import frappe
#from frappe.model.document import Document
from icd_tz.icd_tz.doctype.service_order.service_order import ServiceOrder

class CustomServiceOrder(ServiceOrder):
	def on_submit(self):
		super().on_submit()
		self.create_loading_permit()

	def before_cancel(self):
		super().before_cancel()
		self.check_for_loading_permit()

	def create_loading_permit(self):
		"""
		Create a loading permit document
		"""
		exist_loading_permit = frappe.db.get_all(
			"Loading Permit",
			filters={
				"manifest": self.manifest,
				"container_id": self.container_id
			}
		)
		if len(exist_loading_permit) > 0:
			self.db_set("custom_loading_permit", exist_loading_permit[0].name)
			self.reload()
			return

		inspection_location = frappe.db.get_value(
			"In Yard Container Booking", 
			{"container_id": self.container_id},
			"inspection_location"
		)		
		
		loading_permit = frappe.new_doc("Loading Permit")
		loading_permit.update({
			"manifest": self.manifest,
			"c_and_f_company": self.c_and_f_company,
			"clearing_agent": self.clearing_agent,
			"consignee": self.consignee,
			"container_id": self.container_id,
			"container_no": self.container_no,
			"inspection_location": inspection_location,
		})
		loading_permit.save(ignore_permissions=True)
		loading_permit.reload()

		self.db_set("custom_loading_permit", loading_permit.name)
		self.reload()

	def check_for_loading_permit(self):
		orders = frappe.db.get_all(
			"Service Order",
			filters={
				"container_id": self.container_id,
				"docstatus": 1,
				"name": ["!=", self.name]
			}
		)
		if len(orders) > 0:
			return
		
		if not self.custom_loading_permit:
			return

		loading_permit = frappe.get_cached_doc("Loading Permit", self.custom_loading_permit)

		self.loading_permit = ""
		
		if loading_permit.docstatus == 1:
			loading_permit.cancel()
		
		loading_permit.delete(ignore_permissions=True, force=True)
		self.db_set("custom_loading_permit", "")

	def get_services(self):
		settings_doc = frappe.get_cached_doc("ICD TZ Settings")

		self.get_reception_services(settings_doc)
		self.get_booking_services(settings_doc)
		#self.get_corridor_services(settings_doc)
		self.get_other_charges()		

	def get_reception_services(self, settings_doc):
		if not self.container_id:
			return
		container_doc = frappe.get_doc("Container", self.container_id)
		is_dg = True if container_doc.custom_dangerous_goods==1 else False
		container_reception = frappe.db.get_value(
			"Container",
			self.container_id,
			"container_reception"
		)
		
		reception_details = frappe.get_cached_value(
			"Container Reception",
			container_reception,
			[
				"cargo_type", "has_transport_charges", "t_sales_invoice",
				#"has_shore_handling_charges", 
				"s_sales_invoice"
			],
			as_dict=True
		)
		if not reception_details:
			return
		
		cargo_type=reception_details.cargo_type

		service_names = [row.get("service") for row in self.get("services")]
		if reception_details.has_transport_charges == "Yes":
			transport_item = None
			transport_paid = True if reception_details.t_sales_invoice else False

			""" if self.container_status == "LCL":
				for row in settings_doc.loose_types:
					if is_dg and row.service_type == "DG-Transfer":
						transport_paid = False
						transport_item = row.service_name
						break
					elif not is_dg and row.service_type == "Transfer":
						transport_paid = False
						transport_item = row.service_name
						break
					
			elif """
			if (
				not reception_details.t_sales_invoice and
				self.container_status != "LCL" and 
				cargo_type.lower()!="transit"
			):
				for row in settings_doc.service_types:
					if (
						not is_dg and
						row.service_type == "Transfer" #and row.cargo_type == cargo_type
					):
						transport_item = row.service_name
						transport_paid = False
						break
					elif (
						is_dg and
                        row.service_type == "DG-Transfer" #and row.cargo_type == cargo_type
					):
						transport_item = row.service_name
						transport_paid = False
						break
				
				if not transport_item and not transport_paid:
					frappe.throw("Transfer Pricing Criteria is not set in ICD TZ Settings, Please set it to continue")
			
				if transport_item and transport_item not in service_names:
					self.append("services", {
					"service": transport_item,
					"qty": self.gross_volume if self.container_status == "LCL" else 1
				})
			
		
		if is_dg:#reception_details.has_shore_handling_charges == "Yes":
			dg_charge_item = None
			dg_charge_paid = True if reception_details.s_sales_invoice else False

			if self.container_status == "LCL":
				for row in settings_doc.loose_types:
					if (
						row.service_type == "DG-Charge"
						and row.cargo_type == cargo_type
					):
						dg_charge_paid = False
						dg_charge_item = row.service_name
						break
			elif (
				not reception_details.s_sales_invoice and
				self.container_status != "LCL"
			):
				for row in settings_doc.service_types:
					if (
						row.service_type == "DG-Charge" and
						row.cargo_type == cargo_type
						
					):
						if "2" in str(row.size)[0] and "2" in str(self.container_size)[0]:
							dg_charge_paid = False
							dg_charge_item = row.service_name
							break

						elif "4" in str(row.size)[0] and "4" in str(self.container_size)[0]:
							dg_charge_paid = False
							dg_charge_item = row.service_name
							break

						else:
							continue
			
			if not dg_charge_item and not dg_charge_paid:
				frappe.throw(
					f"DG Charges Pricing Criteria for Size: {self.container_size}, Port: {self.port} and Cargo Type: {reception_details.cargo_type} is not set in ICD TZ Settings, Please set it to continue"
				)
			
			if dg_charge_item and dg_charge_item not in service_names:
				self.append("services", {
					"service": dg_charge_item,
					"qty": self.gross_volume if self.container_status == "LCL" else 1,
					#"remarks": f"Size: <b>{self.container_size}</b>, Cargo Type: <b>{reception_details.cargo_type}</b>, Port: <b>{self.port}</b>"
				})
		
	def get_booking_services(self, settings_doc):
		if not self.container_id:
			return

		booking_details = frappe.db.get_all(
			"In Yard Container Booking",
            {"container_id": self.container_id, "docstatus": 1},
            [
				#"has_stripping_charges",
			  "s_sales_invoice", "has_custom_verification_charges", "cv_sales_invoice"],
		)
		if len(booking_details) == 0:
			return
		container_doc = frappe.get_doc("Container", self.container_id)
		is_dg = True if container_doc.custom_dangerous_goods==1 else False

		container_reception = frappe.db.get_value(
			"Container",
			self.container_id,
			"container_reception"
		)
		
		reception_details = frappe.get_cached_value(
			"Container Reception",
			container_reception,
			[
				"cargo_type"
			],
			as_dict=True
		)
		if not reception_details:
			return
		
		cargo_type=reception_details.cargo_type
		
		strips = []
		verifications = []
		for booking in booking_details:
			#stripping_paid = True if booking.s_sales_invoice else False
			verification_paid = True if booking.cv_sales_invoice else False

			""" if (
				not booking.s_sales_invoice and
				booking.has_stripping_charges == "Yes"
			):
				stripping_item = None

				if self.container_status == "LCL":
					for row in settings_doc.loose_types:
						if row.service_type == "Stripping":
							stripping_paid = False
							stripping_item = row.service_name
							break
				else:
					for row in settings_doc.service_types:
						if row.service_type == "Stripping":
							if "2" in str(row.size)[0] and "2" in str(self.container_size)[0]:
								stripping_paid = False
								stripping_item = row.service_name
								break

							elif "4" in str(row.size)[0] and "4" in str(self.container_size)[0]:
								stripping_paid = False
								stripping_item = row.service_name
								break

							else:
								continue
						
				if not stripping_item and not stripping_paid:
					frappe.throw(f"Stripping Pricing Criteria for Size: {self.container_size} is not set in ICD TZ Settings, Please set it to continue")
				
				strips.append(stripping_item) """
			
			if (
				not booking.cv_sales_invoice and
				booking.has_custom_verification_charges == "Yes" and 
				cargo_type.lower()!="transit"
			):
				verification_item = None
				if self.container_status == "LCL":
					for row in settings_doc.loose_types:
						if not is_dg and row.service_type == "Verification":
							verification_paid = False
							verification_item = row.service_name
							break
						elif is_dg and row.service_type == "DG-Verification":
							verification_paid = False
							verification_item = row.service_name
							break
				else:
					for row in settings_doc.service_types:
						if not is_dg and row.service_type == "Verification":
							if "2" in str(row.size)[0] and "2" in str(self.container_size)[0]:
								verification_paid = False
								verification_item = row.service_name
								break

							elif "4" in str(row.size)[0] and "4" in str(self.container_size)[0]:
								verification_paid = False
								verification_item = row.service_name
								break

							else:
								continue
						elif is_dg and row.service_type == "DG-Verification":
							if "2" in str(row.size)[0] and "2" in str(self.container_size)[0]:
								verification_paid = False
								verification_item = row.service_name
								break

							elif "4" in str(row.size)[0] and "4" in str(self.container_size)[0]:
								verification_paid = False
								verification_item = row.service_name
								break

							else:
								continue
						
					if not verification_item and not verification_paid:
						frappe.throw(f"Custom Verification Pricing criteria for Size: {self.container_size} is not set in ICD TZ Settings, Please set it to continue")
				
					verifications.append(verification_item)
		
		""" if len(strips) > 0:
			self.append("services", {
				"service": strips[0],
				"qty": len(strips) * self.gross_volume if self.container_status == "LCL" else len(strips),
				"remarks": "<b>Having multiple bookings</b>" if len(strips) > 1 else ""
			}) """
		
		if len(verifications) > 0:
			self.append("services", {
				"service": verifications[0],
				"qty": len(verifications) * self.gross_volume if self.container_status == "LCL" else len(verifications),
				"remarks": "<b>Having multiple bookings</b>" if len(verifications) > 1 else ""
			})	
	
	def get_other_charges(self):
		if not self.container_id:
			return
		
		inspeactions = frappe.db.get_all(
			"Container Inspection",
			{"container_id": self.container_id, "docstatus": 1},
			["name"]
		)
		if len(inspeactions) == 0:
			return

		insp_service_dict = {}
		for inspection in inspeactions:
			inspection_doc = frappe.get_doc("Container Inspection", inspection.name)

			for d in inspection_doc.get("services"):
				if d.get("sales_invoice"):
					continue

				if "verification" in str(d.get("service")).lower():
					continue

				if not d.get("service"):
					continue
					
				qty_to_add = self.gross_volume if self.container_status == "LCL" else 1
				if d.get("service") in insp_service_dict:
					insp_service_dict[d.get("service")]["qty"] += qty_to_add
					insp_service_dict[d.get("service")]["remarks"] = 	"<b>Having Multiple Inspections</b>"
				else:
					new_row = {
						"service": d.get("service"),
						"qty": qty_to_add
					}
					insp_service_dict[d.get("service")] = new_row

		for item in insp_service_dict.values():
			self.append("services", item)	
	
