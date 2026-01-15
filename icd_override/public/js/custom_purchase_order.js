erpnext.buying.setup_buying_controller();

frappe.ui.form.on("Purchase Order", {
    refresh(frm) {
        //debugger;
		//console.log("custom code");
        /* frm.add_custom_button(__('Custom Action'), function() {
            frappe.msgprint('Custom Action Clicked');
        }, __('Get Manifest Items')); */
		
	} 
});