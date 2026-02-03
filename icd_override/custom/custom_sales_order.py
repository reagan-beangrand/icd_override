import frappe
from icd_tz.icd_tz.doctype.service_order.service_order import get_container_days_to_be_billed

def get_storage_services(m_bl_no=None, h_bl_no=None):
    if not m_bl_no and not h_bl_no:
        frappe.throw("Please enter either M BL No or H BL No")
        return

    services = []

    filters={}
    if h_bl_no:
        filters["h_bl_no"] = h_bl_no
        filters["has_hbl"] = 1
    elif m_bl_no:
        filters["m_bl_no"] = m_bl_no
        filters["has_hbl"] = 0

    containers = frappe.db.get_all(
        "Container", filters=filters,
        fields=["name", "days_to_be_billed"]
    )
    if len(containers) == 0:
        return

    settings_doc = frappe.get_cached_doc("ICD TZ Settings")

    for container in containers:
        if container.days_to_be_billed == 0:
            continue
        
        container_doc = frappe.get_doc("Container", container.name)
        #is_dg = True if container_doc.custom_dangerous_goods == 1 else False#reagan
        #is_abnormal= True if container_doc.custom_abnormal_load == 1 else False
        is_reefer= True if container_doc.plug_type_of_reefer == 'Y' else False

        if(is_reefer):
            reefer_single_days, reefer_double_days = get_reefer_container_days_to_be_billed(
                container_doc,
                settings_doc
            )

        single_days, double_days = get_container_days_to_be_billed(
            container_doc,
            settings_doc
        )

        if is_reefer:
            reefer_plugin_single_item = None
            reefer_plugin_double_item = None

            if container_doc.freight_indicator == "FCL" and len(reefer_single_days) > 0:                
                for row in settings_doc.service_types:
                    if row.service_type == "Reefer-Plugin-Single":
                        if "2" in str(row.size)[0] and "2" in str(container_doc.size)[0]:
                            reefer_plugin_single_item = row.service_name
                            break

                        elif "4" in str(row.size)[0] and "4" in str(container_doc.size)[0]:
                            reefer_plugin_single_item = row.service_name
                            break

                        else:
                            continue
            if not reefer_plugin_single_item:
                frappe.throw(
                    f"Reefer Plugin-Single Pricing Criteria for Size: {container_doc.size} is not set in ICD TZ Settings, Please set it to continue"
                )
            
            if len(reefer_single_days) > 0:
                new_row = {
                    'item_code': reefer_plugin_single_item,
                    'qty': container_doc.gross_volume if container_doc.freight_indicator == "FCL" else len(reefer_single_days),
                    'container_no': container_doc.container_no,
                    'container_id': container_doc.name,
                    "container_child_refs": ",".join(reefer_single_days)
                }

                services.append(new_row)
            
            if container_doc.freight_indicator == "FCL" and len(reefer_double_days) > 0:                
                for row in settings_doc.service_types:
                    if row.service_type == "Reefer-Plugin-Double":
                        if "2" in str(row.size)[0] and "2" in str(container_doc.size)[0]:
                            reefer_plugin_double_item = row.service_name
                            break

                        elif "4" in str(row.size)[0] and "4" in str(container_doc.size)[0]:
                            reefer_plugin_double_item = row.service_name
                            break

                        else:
                            continue
            if not reefer_plugin_double_item:
                frappe.throw(
                    f"Reefer Plugin-Double Pricing Criteria for Size: {container_doc.size} is not set in ICD TZ Settings, Please set it to continue"
                )
            
            if len(reefer_double_days) > 0:
                new_row = {
                    'item_code': reefer_plugin_double_item,
                    'qty': len(reefer_double_days), #* container_doc.gross_volume if container_doc.freight_indicator == "FCL" else len(reefer_single_days),
                    'container_no': container_doc.container_no,
                    'container_id': container_doc.name,
                    "container_child_refs": ",".join(reefer_single_days)
                }

                services.append(new_row)

        if container_doc.has_single_charge == 1:
            single_storage_item = None

            if container_doc.freight_indicator == "LCL":
                for row in settings_doc.loose_types:
                    if row.service_type == "Storage-Single":# and is_dg==False and is_abnormal==False and is_reefer==False:
                        single_storage_item = row.service_name
                        break
                    """ elif row.service_type == "DG-Storage-Single" and is_dg==True and is_abnormal==False and is_reefer==False:
                        single_storage_item = row.service_name
                        break
                    elif row.service_type == "Abnormal-Storage-Single" and is_dg==False and is_abnormal==True and is_reefer==False:
                        single_storage_item = row.service_name
                        break
                    elif row.service_type == "Reefer-Storage-Single" and is_dg==False and is_abnormal==False and is_reefer==True:
                        single_storage_item = row.service_name
                        break """
            else:
                for row in settings_doc.service_types:
                    if row.service_type == "Storage-Single":# and is_dg==False and is_abnormal==False and is_reefer==False:
                        if "2" in str(row.size)[0] and "2" in str(container_doc.size)[0]:
                            single_storage_item = row.service_name
                            break

                        elif "4" in str(row.size)[0] and "4" in str(container_doc.size)[0]:
                            single_storage_item = row.service_name
                            break

                        else:
                            continue
                    """ elif row.service_type == "DG-Storage-Single" and is_dg==True and is_abnormal==False and is_reefer==False:
                        if "2" in str(row.size)[0] and "2" in str(container_doc.size)[0]:
                            single_storage_item = row.service_name
                            break

                        elif "4" in str(row.size)[0] and "4" in str(container_doc.size)[0]:
                            single_storage_item = row.service_name
                            break

                        else:
                            continue
                    elif row.service_type == "Abnormal-Storage-Single" and is_dg==False and is_abnormal==True and is_reefer==False:
                        if "2" in str(row.size)[0] and "2" in str(container_doc.size)[0]:
                            single_storage_item = row.service_name
                            break

                        elif "4" in str(row.size)[0] and "4" in str(container_doc.size)[0]:
                            single_storage_item = row.service_name
                            break

                        else:
                            continue
                    elif row.service_type == "Reefer-Storage-Single" and is_dg==False and is_abnormal==False and is_reefer==True:
                        if "2" in str(row.size)[0] and "2" in str(container_doc.size)[0]:
                            single_storage_item = row.service_name
                            break

                        elif "4" in str(row.size)[0] and "4" in str(container_doc.size)[0]:
                            single_storage_item = row.service_name
                            break

                        else:
                            continue """
                
            if not single_storage_item:
                frappe.throw(
                    f"Storage-Single Pricing Criteria for Size: {container_doc.size} is not set in ICD TZ Settings, Please set it to continue"
                )
            
            if len(single_days) > 0:
                new_row = {
                    'item_code': single_storage_item,
                    'qty': len(single_days) * container_doc.gross_volume if container_doc.freight_indicator == "LCL" else len(single_days),
                    'container_no': container_doc.container_no,
                    'container_id': container_doc.name,
                    "container_child_refs": ",".join(single_days)
                }

                services.append(new_row)
        
        if container_doc.has_double_charge == 1:
            double_storage_item = None

            if container_doc.freight_indicator == "LCL":
                for row in settings_doc.loose_types:
                    if row.service_type == "Storage-Double":# and is_dg==False and is_abnormal==False and is_reefer==False:
                        double_storage_item = row.service_name
                        break
                    """ elif row.service_type == "DG-Storage-Double" and is_dg==True and is_abnormal==False and is_reefer==False:
                        double_storage_item = row.service_name
                        break
                    elif row.service_type == "Abnormal-Storage-Double" and is_dg==False and is_abnormal==True and is_reefer==False:
                        double_storage_item = row.service_name
                        break
                    elif row.service_type == "Reefer-Storage-Double" and is_dg==False and is_abnormal==False and is_reefer==True:
                        double_storage_item = row.service_name
                        break """

            else:
                for row in settings_doc.service_types:
                    if row.service_type == "Storage-Double":# and is_dg==False and is_abnormal==False and is_reefer==False:
                        if "2" in str(row.size)[0] and "2" in str(container_doc.size)[0]:
                            double_storage_item = row.service_name
                            break

                        elif "4" in str(row.size)[0] and "4" in str(container_doc.size)[0]:
                            double_storage_item = row.service_name
                            break

                        else:
                            continue
                    """ elif row.service_type == "DG-Storage-Double" and is_dg==True and is_abnormal==False and is_reefer==False:
                        if "2" in str(row.size)[0] and "2" in str(container_doc.size)[0]:
                            double_storage_item = row.service_name
                            break

                        elif "4" in str(row.size)[0] and "4" in str(container_doc.size)[0]:
                            double_storage_item = row.service_name
                            break

                        else:
                            continue
                    elif row.service_type == "Abnormal-Storage-Double" and is_dg==True and is_abnormal==False and is_reefer==False:
                        if "2" in str(row.size)[0] and "2" in str(container_doc.size)[0]:
                            double_storage_item = row.service_name
                            break

                        elif "4" in str(row.size)[0] and "4" in str(container_doc.size)[0]:
                            double_storage_item = row.service_name
                            break

                        else:
                            continue
                    elif row.service_type == "Reefer-Storage-Double" and is_dg==True and is_abnormal==False and is_reefer==False:
                        if "2" in str(row.size)[0] and "2" in str(container_doc.size)[0]:
                            double_storage_item = row.service_name
                            break

                        elif "4" in str(row.size)[0] and "4" in str(container_doc.size)[0]:
                            double_storage_item = row.service_name
                            break

                        else:
                            continue """
            
            if not double_storage_item:
                frappe.throw(
                    f"Storage-Double Pricing Criteria for Size: {container_doc.size} is not set in ICD TZ Settings, Please set it to continue"
                )
            
            if len(double_days) > 0:
                new_row = {
                    'item_code': double_storage_item,
                    'qty': len(double_days) * container_doc.gross_volume if container_doc.freight_indicator == "LCL" else len(double_days),
                    'container_no': container_doc.container_no,
                    'container_id': container_doc.name,
                    "container_child_refs": ",".join(double_days)
                }

                services.append(new_row)
        
        if (
            not container_doc.r_sales_invoice and
            container_doc.has_removal_charges == "Yes"
        ):
            removal_item = None
            
            if container_doc.freight_indicator == "LCL":
                for row in settings_doc.loose_types:
                    if row.service_type == "Removal":
                        removal_item = row.service_name
                        break
            else:
                for row in settings_doc.service_types:
                    if row.service_type == "Removal":
                        if "2" in str(row.size)[0] and "2" in str(container_doc.size)[0] and row.cargo_type==container_doc.cargo_type:
                            removal_item = row.service_name
                            break

                        elif "4" in str(row.size)[0] and "4" in str(container_doc.size)[0] and row.cargo_type==container_doc.cargo_type:
                            removal_item = row.service_name
                            break

                        else:
                            continue
            
            if not removal_item:
                frappe.throw(
                    f"Removal Pricing Criteria for Size: {container_doc.size} is not set in ICD TZ Settings, Please set it to continue"
                )
            
            services.append({
                'item_code': removal_item,
                'qty': container_doc.gross_volume if container_doc.freight_indicator == "LCL" else 1,
                'container_no': container_doc.container_no,
                'container_id': container_doc.name,
            })
                
    return services

def get_reefer_container_days_to_be_billed(container_doc, settings_doc):
    single_days = []
    double_days = []
    no_of_single_days = 0
    no_of_double_days = 0
    single_charge_count = 0
    double_charge_count = 0

    for d in settings_doc.storage_days:        
        if d.destination.lower() == "reefer":
            if d.charge == "Single":
                no_of_single_days = d.get("to") - d.get("from") + 1

            elif d.charge == "Double":
                no_of_double_days = d.get("to") - d.get("from") + 1
                
    for row in container_doc.container_dates:
        if (
            row.is_billable == 1 and
            container_doc.has_single_charge == 1 and
            single_charge_count < no_of_single_days
        ):
            single_days.append(row)
            single_charge_count += 1
        
        elif (
            row.is_billable == 1 and
            container_doc.has_double_charge == 1 and
            single_charge_count >= no_of_single_days and
            double_charge_count <= no_of_double_days
        ):
            double_days.append(row)
            double_charge_count += 1
    
    single_days = [row.name for row in single_days if not row.sales_invoice]
    double_days = [row.name for row in double_days if not row.sales_invoice]
    return single_days, double_days