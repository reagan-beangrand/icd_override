
frappe.ui.form.on('Purchase Order', {
	update_items: (frm) => {
        if (!frm.doc.m_bl_no && !frm.doc.h_bl_no) {
            frappe.msgprint("Please enter M BL No or H BL No")
            return;
        }

        if (frm.is_dirty()) {
            frappe.msgprint("Please save the document before updating items")
            return;
        }

        frappe.call({
            method: 'icd_override.custom.custom_purchase_order.update_items_on_purchase_order',
            args: {
                doc_name: frm.doc.name
            },
            freeze: true,
            freeze_message: __('<i class="fa fa-spinner fa-spin fa-4x"></i>'),
            callback: (r) => {
                if (r.message) {
                    frm.reload_doc();
                }
            }
        });
    }
});