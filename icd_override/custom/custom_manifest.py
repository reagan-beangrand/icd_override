import frappe
from openpyxl import load_workbook
from datetime import datetime
from icd_tz.icd_tz.doctype.manifest.manifest import Manifest

class CustomManifest(Manifest):
    @frappe.whitelist()
    def extract_data_from_manifest_file(self):
        #frappe.msgprint("ICD_TZ  OVERRIDE- Extracting data from manifest file...")
        if self.manifest:
            file_url = self.manifest
            file_path = frappe.get_site_path('private', 'files', file_url.split('/files/')[-1])
            
            # Load the Excel file
            workbook = load_workbook(file_path, data_only=True)

            # Function to convert dates
            def convert_date(excel_date):
                if isinstance(excel_date, datetime):
                    return excel_date.strftime('%Y-%m-%d')
                if isinstance(excel_date, str):
                    try:
                        return datetime.strptime(excel_date, '%d/%m/%Y').strftime('%Y-%m-%d')
                    except ValueError:
                        return None
                return None

            # Process the MRN Detail (1) sheet
            vessel_info_sheet = workbook['MRN Detail (1)']
            vessel_info_row = next(vessel_info_sheet.iter_rows(min_row=4, values_only=True))
            self.mrn = vessel_info_row[0]
            self.vessel_name = vessel_info_row[1]
            self.call_sign = vessel_info_row[2]
            self.voyage_no = vessel_info_row[3]
            self.custom_departure_date = convert_date(vessel_info_row[4])        
            self.arrival_date = convert_date(vessel_info_row[5])
            self.tpa_uid = vessel_info_row[6]

            # Process the Container (2) sheet
            containers_sheet = workbook['Container (2)']            
            self.containers = []
            for row in containers_sheet.iter_rows(min_row=4, values_only=True):
                container = self.append("containers", {})
                container.m_bl_no = row[0]
                container.type_of_container = row[1]
                container.container_no = row[2]
                container.container_size = row[3]
                container.seal_no1 = row[4]
                container.seal_no2 = row[5]
                container.seal_no3 = row[6]
                container.freight_indicator = row[7]
                container.no_of_packages = row[8]
                container.package_unit = row[9]                
                container.weight = row[10]
                container.weight_unit = row[11]
                container.plug_type_of_reefer = row[12]
                container.minimum_temperature = row[13]
                container.maximum_temperature = row[14]

            # Process the HBL Container (3) sheet
            hbl_containers_sheet = workbook['HBL Container (3)']            
            self.hbl_containers = []
            for row in hbl_containers_sheet.iter_rows(min_row=4, values_only=True):
                hbicontainer = self.append("hbl_containers", {})
                hbicontainer.m_bl_no = row[0]
                hbicontainer.h_bl_no = row[1]
                hbicontainer.type_of_container = row[2]
                hbicontainer.container_no = row[3]
                hbicontainer.container_size = row[4]
                hbicontainer.seal_no1 = row[5]
                hbicontainer.seal_no2 = row[6]
                hbicontainer.seal_no3 = row[7]
                hbicontainer.freight_indicator = row[8]
                hbicontainer.no_of_packages = row[9]
                hbicontainer.package_unit = row[10]               
                hbicontainer.weight = row[11]
                hbicontainer.weight_unit = row[12]
                hbicontainer.plug_type_of_reefer = row[13]
                hbicontainer.minimum_temperature = row[14]
                hbicontainer.maximum_temperature = row[15]
            
            # Process the Master BL List (4) sheet
            master_bl_sheet = workbook['Master BL List (4)']            
            self.master_bl = []
            filtered_rows_data = []
            target_value = "WITZDL034" #PMM ICD number
            for row in master_bl_sheet.iter_rows(min_row=4, values_only=True):                
                if row[4] == target_value:
                    filtered_rows_data.append(row)
                
            for filtered_row in filtered_rows_data:
                master_bl = self.append("master_bl", {})
                master_bl.m_bl_no = filtered_row[0]
                master_bl.cargo_classification = filtered_row[1]
                master_bl.bl_type = filtered_row[2]
                master_bl.place_of_destination = filtered_row[3]
                master_bl.place_of_delivery = filtered_row[4]
                master_bl.oil_type = filtered_row[5]
                master_bl.port_of_loading = filtered_row[6]
                master_bl.number_of_containers = filtered_row[7]
                master_bl.cargo_description = filtered_row[8]
                master_bl.number_of_package = filtered_row[9]
                master_bl.package_unit = filtered_row[10]
                master_bl.gross_weight = filtered_row[11]
                master_bl.gross_weight_unit = filtered_row[12]
                master_bl.gross_volume = filtered_row[13]
                master_bl.gross_volume_unit = filtered_row[14]
                master_bl.invoice_value = filtered_row[15]
                master_bl.invoice_currency = filtered_row[16]
                master_bl.freight_charge = filtered_row[17]
                master_bl.freight_currency = filtered_row[18]
                master_bl.imdg_code = filtered_row[19]
                master_bl.packing_type = filtered_row[20]
                master_bl.shipping_agent_code = filtered_row[21]
                master_bl.shipping_agent_name = filtered_row[22]
                master_bl.forwarder_code = filtered_row[23]
                master_bl.forwarder_name = filtered_row[24]
                master_bl.forwarder_tel = filtered_row[25]
                master_bl.exporter_name = filtered_row[26]
                master_bl.exporter_tel = filtered_row[27]
                master_bl.exporter_address = filtered_row[28]
                master_bl.exporter_tin = filtered_row[29]
                master_bl.consignee_name = filtered_row[30]
                master_bl.consignee_tel = filtered_row[31]
                master_bl.consignee_address = filtered_row[32]
                master_bl.consignee_tin = filtered_row[33]
                master_bl.notify_name = filtered_row[34]
                master_bl.notify_tel = filtered_row[35]
                master_bl.notify_address = filtered_row[36]
                master_bl.notify_tin = filtered_row[37]
                master_bl.shipping_mark = filtered_row[38]
                master_bl.net_weight = filtered_row[39]
                master_bl.net_weight_unit = filtered_row[40]

            # Process the House BL List (5) sheet
            house_bl_sheet = workbook['House BL List (5)']
            self.update_house_bl_details(house_bl_sheet)
        
            # self.save()
            return False