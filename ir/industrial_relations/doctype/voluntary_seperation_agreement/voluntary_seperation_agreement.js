// Copyright (c) 2024, BuFf0k and contributors
// For license information, please see license.txt

frappe.ui.form.on("Voluntary Seperation Agreement", {
    refresh: function(frm) {
        // Check the flag before triggering the handler
        if (frm.doc.linked_disciplinary_action && !frm.doc.linked_disciplinary_action_processed) {
            frm.trigger('linked_disciplinary_action');
        };
        
        frm.fields_dict['payment_details'].grid.wrapper.on('change', 'input[data-fieldname="value"]', function() {
            calculate_total(frm);
        });
    },

    linked_disciplinary_action: function(frm) {
        if (frm.doc.linked_disciplinary_action) {
            frappe.call({
                method: 'ir.industrial_relations.doctype.voluntary_seperation_agreement.voluntary_seperation_agreement.fetch_disciplinary_action_data',
                args: {
                    disciplinary_action: frm.doc.linked_disciplinary_action
                },
                callback: function(r) {
                    if (r.message) {
                        const data = r.message;

                        // Directly update the doc and refresh fields without triggering events
                        frm.doc.employee = data.accused || '';
                        frm.doc.names = data.accused_name || '';
                        frm.doc.coy = data.accused_coy || '';
                        frm.doc.position = data.accused_pos || '';
                        frm.doc.company = data.company || '';

                        frm.refresh_field('employee');
                        frm.refresh_field('names');
                        frm.refresh_field('coy');
                        frm.refresh_field('position');
                        frm.refresh_field('company');
                        // Set the flag to prevent refresh loop
                        frm.set_value('linked_disciplinary_action_processed', true);
                    }
                }
            });
        }
    },

    company: function(frm) {
        if (frm.doc.company) {
            frappe.call({
                method: 'ir.industrial_relations.doctype.voluntary_seperation_agreement.voluntary_seperation_agreement.fetch_company_letter_head',
                args: {
                    company: frm.doc.company
                },
                callback: function(r) {
                    if (r.message) {
                        frm.doc.letter_head = r.message.letter_head || '';
                        frm.refresh_field('letter_head');
                    }
                }
            });
        }
    },

    before_submit: function(frm) {
        if (!frm.doc.signed_vsp) {
            frappe.msgprint(__('You cannot submit this document until you have attached a signed copy of the VSP'));
            frappe.validated = false;
        }
    }
});

function calculate_total(frm) {
    let total = 0;
    frm.doc.payment_details.forEach(row => {
        total += row.value;
    });
    frm.set_value('total_gross', total);
}