import frappe
from time import sleep
from frappe.utils import nowdate

@frappe.whitelist()
def update_items_on_purchase_order(doc_name):
    doc = frappe.get_doc("Purchase Order", doc_name)

    items = []
    unique_containers = []
    for item in doc.items:
        if item.container_id not in unique_containers:
            unique_containers.append(item.container_id)
    
    for container_id in unique_containers:
        container_doc = frappe.get_doc("Container", container_id)
        container_doc.update_container_stay(up_to_date=doc.delivery_date)
        container_doc.reload()

    sleep(10)

    """ items += get_storage_services(doc.m_bl_no, doc.h_bl_no)

    service_order_items, service_docs = get_service_order_items(m_bl_no=doc.m_bl_no, h_bl_no=doc.h_bl_no)
    items += service_order_items

    
    if len(service_docs) > 0:
        source_doc = service_docs[0]

        if not doc.consignee:
            doc.consignee = source_doc.consignee
        
        if not doc.company:
            doc.company = source_doc.company
        
        if not doc.c_and_f_company:
            doc.c_and_f_company = source_doc.c_and_f_company
        
        if not doc.m_bl_no:
            doc.m_bl_no = source_doc.m_bl_no
        
        if not doc.h_bl_no:
            doc.h_bl_no = source_doc.h_bl_no

    for record in service_docs:
        record.db_set("sales_order", doc.name)
    
    doc.items = []
    for item in items:
        doc.append("items", item)
    
    doc.save(ignore_permissions=True)
    doc.reload() """
    return True

@frappe.whitelist()
def make_purchase_order(
    doc_type=None,
    doc_name=None,
    m_bl_no=None,
    h_bl_no=None
):
    items = []
    company = None
    consignee = None
    c_and_f_company = None
    order_m_bl_no = m_bl_no if m_bl_no else None
    order_h_bl_no = h_bl_no if h_bl_no else None

    settings_doc = frappe.get_cached_doc("ICD TZ Settings")

    #items += get_storage_services(m_bl_no, h_bl_no)

    """ service_order_items, service_docs = get_service_order_items(
        doc_type=doc_type,
        doc_name=doc_name,
        m_bl_no=m_bl_no,
        h_bl_no=h_bl_no
    ) """
    
    #items += service_order_items
    #if len(items) == 0:
    #    return
    
    """ if len(service_docs) > 0:
        source_doc = service_docs[0]

        if not consignee:
            consignee = source_doc.consignee
        
        if not company:
            company = source_doc.company
        
        if not c_and_f_company:
            c_and_f_company = source_doc.c_and_f_company
        
        if not order_m_bl_no:
            order_m_bl_no = source_doc.m_bl_no
        
        if not order_h_bl_no:
            order_h_bl_no = source_doc.h_bl_no
    
    else: """
    if not consignee and h_bl_no:
            consignee = frappe.get_cached_value("Container", {"h_bl_no": h_bl_no}, "consignee")
    if not consignee and m_bl_no:
            consignee = frappe.get_cached_value("Container", {"m_bl_no": m_bl_no}, "consignee")
    
    row_item = {
            'item_code': "Transport Charges",
            'qty': "1",
            'uom': "Nos",
            'rate': 2300
        }
    items.append(row_item)

    purchase_order = frappe.get_doc({
        "doctype": "Purchase Order",
        "supplier":"Tanzania East Africa Gateway Terminal Limited",
        "company": company,
        #"customer": consignee,
        "custom_c_and_f_company": c_and_f_company,
        "transaction_date": nowdate(),
        "delivery_date": nowdate(),
        "buying_price_list": settings_doc.get("custom_default_buying_price_list"),
        "currency": frappe.get_cached_value("Price List", settings_doc.get("custom_default_buying_price_list"), "currency"),
        "items": items,
        "custom_consignee": consignee,
        "schedule_date": nowdate(),
        "custom_m_bl_no": order_m_bl_no,
        "custom_h_bl_no": order_h_bl_no
    })

    
    
    purchase_order.insert()
    purchase_order.set_missing_values()
    purchase_order.calculate_taxes_and_totals()
    purchase_order.save(ignore_permissions=True)
    purchase_order.reload()

    frappe.msgprint(f"Purchase Order <b>{purchase_order.name}</b> created successfully", alert=True)
    return purchase_order.name

@frappe.whitelist()
def create_purchase_order(data):
	data = frappe.parse_json(data)
    
	return make_purchase_order(m_bl_no=data.get("m_bl_no"), h_bl_no=data.get("h_bl_no"))