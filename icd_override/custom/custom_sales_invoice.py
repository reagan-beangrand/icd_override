import frappe
#from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice
from icd_tz.icd_tz.api.sales_invoice import update_container_insp,update_booking_refs, update_container_reception, update_container_refs, update_storage_date_refs



def update_sales_references(self):
        if not self.m_bl_no and not self.h_bl_no:
            return

        invoice_id = self.name
        if self.is_return:
            invoice_id = None

        settings_doc = frappe.get_cached_doc("ICD TZ Settings")
        #corridor_services = [row.service_name for row in settings_doc.service_types if row.service_type == "Levy"]
        verification_services = [row.service_name for row in settings_doc.service_types if row.service_type == "Verification"]
        #stripping_services = [row.service_name for row in settings_doc.service_types if row.service_type == "Stripping"]
        removal_services = [row.service_name for row in settings_doc.service_types if row.service_type == "Removal"]
        transport_services = [row.service_name for row in settings_doc.service_types if row.service_type == "Transfer"]
        storage_services = [row.service_name for row in settings_doc.service_types if row.service_type in ["Storage-Single", "Storage-Double"]]
        #shore_services = [row.service_name for row in settings_doc.service_types if row.service_type == "Shore"]

        # for loose container
        #corridor_services += [row.service_name for row in settings_doc.loose_types if row.service_type == "Levy"]
        verification_services += [row.service_name for row in settings_doc.loose_types if row.service_type == "Verification"]
        #stripping_services += [row.service_name for row in settings_doc.loose_types if row.service_type == "Stripping"]
        removal_services += [row.service_name for row in settings_doc.loose_types if row.service_type == "Removal"]
        transport_services += [row.service_name for row in settings_doc.loose_types if row.service_type == "Transfer"]
        storage_services += [row.service_name for row in settings_doc.loose_types if row.service_type in ["Storage-Single", "Storage-Double"]]
        #shore_services += [row.service_name for row in settings_doc.loose_types if row.service_type == "Shore"]
        
        for item in self.items:
            if item.item_code in transport_services:
                update_container_reception(item.container_id, invoice_id, "t_sales_invoice")
            
            #elif item.item_code in shore_services:
            #    update_container_reception(item.container_id, invoice_id, "s_sales_invoice")
            
            #elif item.item_code in stripping_services:
            #    update_booking_refs(item.container_id, invoice_id, "s_sales_invoice")
            
            elif item.item_code in verification_services:
                update_booking_refs(item.container_id, invoice_id, "cv_sales_invoice")
            
            elif item.item_code in removal_services:
                update_container_refs(item.container_id, invoice_id, "r_sales_invoice")
            
            #elif item.item_code in corridor_services:
            #    update_container_refs(item.container_id, invoice_id, "c_sales_invoice")
            
            elif item.item_code in storage_services:
               update_storage_date_refs(item.container_id, invoice_id, item.container_child_refs)
            
            else:
                update_container_insp(item.container_id, item.item_code, invoice_id)
        
        sales_order = self.items[0].sales_order
        service_orders = frappe.db.get_all(
            "Service Order",
            filters={"sales_order": sales_order},
        )
        for row in service_orders:
            frappe.db.set_value(
                "Service Order",
                row.name,
                "sales_invoice",
                invoice_id
            )
