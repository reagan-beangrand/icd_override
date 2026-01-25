frappe.ui.form.off("Container Inspection","refresh");
frappe.ui.form.off("Container Inspection","onload");
frappe.ui.form.on('Container Inspection', {   
    
    create_sales_order: (frm) => {
		if (!frm.doc.sales_order & frm.doc.docstatus == 1) {
			frm.add_custom_button(__('Create Sales Order'), () => {

				/* frappe.new_doc('Sales Order', {
					"container_inspection": frm.doc.name,
					"consignee": frm.doc.consignee,
					"clearing_agent": frm.doc.c_and_f_agent,
					"c_and_f_company": frm.doc.c_and_f_company,
					"custom_container_id": frm.doc.container_id,
					"custom_container_no": frm.doc.container_no,
					"customer": frm.doc.consignee,
                    "m_bl_no": frm.doc.m_bl_no,
				}, doc => {
				}); */
				debugger;
				var values={
					"m_bl_no":frm.doc.m_bl_no,
					"h_bl_no":frm.doc.h_bl_no,
					"c_and_f_company":frm.doc.c_and_f_company,
					"clearing_agent":frm.doc.c_and_f_agent,
					"consignee":frm.doc.consignee,
					"container_inspection":frm.doc.name,
					"custom_container_id":frm.doc.container_id,
					"custom_container_no":frm.doc.container_no,
					"customer":frm.doc.consignee
				};
				/* if(frm.doc.m_bl_no!=""){
					value=frm.doc.m_bl_no;
				}else if(frm.doc.h_bl_no!=""){
					value=frm.doc.h_bl_no;
				} */
				frappe.call({
                    method: 'icd_tz.icd_tz.api.sales_order.create_sales_order',
                    args: {
                        data: values
                    },
                    freeze: true,
                    freeze_message: __('<i class="fa fa-spinner fa-spin fa-4x"></i>'),
                    callback: (r) => {
                        if (r.message) {
                            d.hide()
                            frappe.show_alert({
                                message: __("Sales Order Created successfully"),
                                indicator: 'green'
                            }, 10);
                        }
                    }
                });
			}).addClass('btn-primary');
		}
	}
});