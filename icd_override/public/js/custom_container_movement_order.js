// Copyright (c) 2024, elius mgani and contributors
// For license information, please see license.txt
frappe.ui.form.off("Container Movement Order","get_containers");
frappe.ui.form.on("Container Movement Order", {
    get_containers: (frm) => {
        if (frm.doc.manifest) {
            frappe.call({
                method: "icd_override.custom.custom_whitelisted.get_manifest_details",
                args: {
                    manifest: frm.doc.manifest
                },
                freeze: true,
                freeze_message: __("Please wait..."),
                callback: (r) => {
                    if (r.message) {
                        let data = r.message;
                        frm.set_value("company", data[0].company);
                        frm.set_value("ship", data[0].vessel_name);
                        frm.set_value("voyage_no", data[0].voyage_no);
                        frm.set_value("ship_dc_date", data[0].arrival_date);

                        frm.refresh_fields();

                        show_dialog(frm, data);
                    }
                }
            });
        }
    },
    
	
});

var show_dialog = (frm, data) => {
    let d = new frappe.ui.Dialog({
        title: __("Select Container"),
        size: "large",
        fields: [
            {
                fieldtype: "Data",
                fieldname: "container_no",
                label: __("Container No"),
                placeholder: __("Enter Container No to filter"),
                /* onchange: function() {
                    console.log('Container No changed'+d.fields_dict.container_no.$input.val());
                    d.fields_dict["container_table"].refresh(); // Refresh the container table when container_no changes
                }, */
                
            },
            /* {
                fieldtype: "Column Break",
                fieldname: "column_break"
            },
            {
                fieldtype: "Button",
                fieldname: "apply_filter",
                label: __("Apply Filter")
            }, */
            {
                fieldtype: "Section Break",
                fieldname: "section_break"
            },
            {
                fieldtype: "HTML",
                fieldname: "container_table",
                /* get_query: function() {
                    debugger;
                    let container_no = d.get_value("container_no") || "";
                    console.log('Getting query for container_no');
                return {
                    
                    // Specify the custom server method
                    query: 'icd_override.custom.custom_whitelisted.get_manifest_details',
                    // Pass additional filters or parameters to the server method
                    filters: {
                        "manifest": frm.doc.manifest,
                        "container_no":container_no// d.get_value("container_no")                      
                    }
                }; 
            }, */
            }
        ]
    });

    let wrapper = d.fields_dict.container_table.$wrapper;

    if (data.length > 0) {
        let data_html = show_details(data);
        wrapper.html(data_html);
        attachCheckboxListener(wrapper);
    }

    /* d.fields_dict.apply_filter.$input.click(() => {
        //debugger;
        get_containers(frm.doc.manifest, d.get_value("container_no"), wrapper);
    }); */

    d.set_primary_action(__("Select"), () => {
        let container = {};

        wrapper.find('tr:has(input:checked)').each(function () {
            container = {
                container_no: $(this).find("#container_no").attr("data-container_no"),
                m_bl_no: $(this).find("#m_bl_no").attr("data-m_bl_no"),
                container_size: $(this).find("#container_size").attr("data-container_size"),
                freight_indicator: $(this).find("#freight_indicator").attr("data-freight_indicator"),
                cargo_type: $(this).find("#cargo_type").attr("data-cargo_type"),
            };
        });

        if (container) {
            frm.set_value("container_no", container.container_no);
            frm.set_value("m_bl_no", container.m_bl_no);
            frm.set_value("size", container.container_size);
            frm.set_value("freight_indicator", container.freight_indicator);
            frm.set_value("cargo_type", container.cargo_type);

            frm.refresh_fields();
            d.hide();
        } else {
            frappe.msgprint({
                title: __('Message'),
                indicator: 'red',
                message: __(
                    '<h4 class="text-center" style="background-color: #D3D3D3; font-weight: bold;">\
                    No any Container selected<h4>'
                )
            });
        }
    });

    d.$wrapper.find('.modal-content').css({
        "width": "750px",
        "max-height": "1000px",
        "overflow": "auto",
    });

    d.show();

    let $model=d.$wrapper.find('.modal-content');
    let $header = $model.find('.modal-header');
    let $footer = $model.find('.modal-footer');

    $footer.find('.btn-primary').appendTo($header).css({
        "float": "right",
        "margin-right": "30px",              
    });
    $footer.remove();
    
    let $input = d.fields_dict.container_no.$input;
    let filter_timeout=null;
    
    $input.on("input", function() {
        let val = $(this).val();
        if(filter_timeout)
            clearTimeout(filter_timeout);

        filter_timeout = setTimeout(() => {
            get_containers(frm.doc.manifest, val, wrapper);
        }, 500);
    });

    function show_details(data) {
        let html = `
            <style>
                .table-container {
                    height: 300px;
                    overflow-y: auto;
                    margin-top: 10px;
                }
                .table-container thead th {
                    position: sticky;
                    top: 0;
                    background-color: white;
                    z-index: 1;
                }
                .table-container table {
                    width: 100%;
                }
                .container-checkbox {
                    transform: scale(1.2);
                    margin: 5px;
                }
            </style>
            <div class="table-container">
                <table class="table table-hover">
                    <colgroup>
                        <col width="5%">
                        <col width="25%">
                        <col width="25%">
                        <col width="10%">
                        <col width="15%">
                        <col width="20%">
                    </colgroup>
                    <thead>
                        <tr>
                            <th style="background-color: #D3D3D3;"></th>
                            <th style="background-color: #D3D3D3;">Container NO</th>
                            <th style="background-color: #D3D3D3;">M BL No</th>
                            <th style="background-color: #D3D3D3;">Size</th>
                            <th style="background-color: #D3D3D3;">Freight Indicator</th>
                            <th style="background-color: #D3D3D3;">Cargo Type</th>
                        </tr>
                    </thead>
                    <tbody>`;

        data.forEach(row => {
            let cargo_type = ''
            if (row.cargo_type == 'IM') {
                cargo_type = 'Local'
            } else if (row.cargo_type == 'TR') {
                cargo_type = 'Transit'
            }
            html += `<tr>
                    <td><input type="checkbox" class="container-checkbox"/></td>
                    <td id="container_no" data-container_no="${row.container_no}">${row.container_no}</td>
                    <td id="m_bl_no" data-m_bl_no="${row.m_bl_no}">${row.m_bl_no}</td>
                    <td id="container_size" data-container_size="${row.container_size}">${row.container_size}</td>
                    <td id="freight_indicator" data-freight_indicator="${row.freight_indicator}">${row.freight_indicator}</td>
                    <td id="cargo_type" data-cargo_type="${cargo_type}">${cargo_type}</td>
                </tr>`;
        });

        html += `</tbody></table></div>`;
        return html;
    }

    function get_containers(manifest, container_no, wrapper) {
        frappe.call({
            method: "icd_override.custom.custom_whitelisted.get_manifest_details",
            args: {
                manifest: manifest,
                container_no: container_no
            },
            freeze: true,
            freeze_message: __("Filtering containers..."),
            callback: (r) => {
                let records = r.message;
                if (records.length > 0) {
                    let html = show_details(records);
                    wrapper.html(html);
                    attachCheckboxListener(wrapper); 
                } else {
                    wrapper.html("");
                    wrapper.append(`<div class="multiselect-empty-state"
                        style="border: 1px solid #d1d8dd; border-radius: 3px; height: 200px; overflow: auto;">
                        <span class="text-center" style="margin-top: -40px;">
                            <i class="fa fa-2x fa-heartbeat text-extra-muted"></i>
                            <p class="text-extra-muted text-center" style="font-size: 16px; font-weight: bold;">
                            No Container(s) found</p>
                        </span>
                    </div>`);
                }
            }
        });
    }

    function attachCheckboxListener(wrapper) {
        wrapper.find('.container-checkbox').on('click', function () {
            wrapper.find('.container-checkbox').not(this).prop('checked', false);
        });
    }
};
