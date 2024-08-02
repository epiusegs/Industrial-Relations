// Copyright (c) 2024, BuFf0k and contributors
// For license information, please see license.txt

frappe.ui.form.on('Warning Form', {
    refresh: function(frm) {
        // Manually trigger the linked_disciplinary_action handler if the field is already set
        if (frm.doc.linked_disciplinary_action) {
            frm.trigger('linked_disciplinary_action');
        }
    
    	// Manually trigger the applied_rights handler if the field is already set
        if (frm.doc.applied_rights) {
            frm.trigger('applied_rights');
        }
    },
    
    linked_disciplinary_action: function(frm) {
        if (frm.doc.linked_disciplinary_action) {
            // Fetch accused field from Disciplinary Action document and enter into employee field
            frappe.db.get_value('Disciplinary Action', frm.doc.linked_disciplinary_action, 'accused', (r) => {
                frm.set_value('employee', r ? r.accused : '');
            });
        
        	// Fetch accused_name field from Disciplinary Action document and enter into names field
            frappe.db.get_value('Disciplinary Action', frm.doc.linked_disciplinary_action, 'accused_name', (r) => {
                frm.set_value('names', r ? r.accused_name : '');
            });
        
            // Fetch accused_coy field from Disciplinary Action document and enter into coy field
            frappe.db.get_value('Disciplinary Action', frm.doc.liniked_disciplinary_action, 'accused_coy', (r) => {
                frm.set_value('coy', r ? r.accused_coy : '');
            });
        
            // Fetch accused_pos field from Disciplinary Action document and enter into position field
            frappe.db.get_value('Disciplinary Action', frm.doc.linked_disciplinary_action, 'accused_pos', (r) => {
                frm.set_value('position', r ? r.accused_pos : '');
            });

            // Fetch company field from Disciplinary Action document and enter into company field
            frappe.db.get_value('Disciplinary Action', frm.doc.linked_disciplinary_action, 'company', (r) => {
                frm.set_value('company', r ? r.company : '');
            });

            // Fetch data from previous_disciplinary_outcomes and enter into disciplinary_history field
            frappe.model.with_doc('Disciplinary Action', frm.doc.linked_disciplinary_action, function() {
                let doc = frappe.get_doc('Disciplinary Action', frm.doc.linked_disciplinary_action);
                frm.clear_table('disciplinary_history');
                $.each(doc.previous_disciplinary_outcomes, function(_, row) {
                    let child = frm.add_child('disciplinary_history');
                    child.disc_action = row.disc_action;
                    child.date = row.date;
                    child.sanction = row.sanction;
                    child.charges = row.charges;
                });
                frm.refresh_field('disciplinary_history');

                // Fetch data from final_charges and enter into warning_charges field
                frm.clear_table('warning_charges');
                $.each(doc.final_charges, function(_, row) {
                    let child = frm.add_child('warning_charges');
                    child.indiv_charge = `(${row.code_item}) ${row.charge}`;
                });
                frm.refresh_field('warning_charges');
            });
        }
    },

    company: function(frm) {
        if (frm.doc.company) {
            // Fetch default_letter_head field from Company document and enter into letter_head field
            frappe.db.get_value('Company', frm.doc.company, 'default_letter_head', (r) => {
                frm.set_value('letter_head', r ? r.default_letter_head : '');
            });
        }
    },

	applied_rights: function(frm) {
        if (frm.doc.applied_rights) {
            // Fetch data from Employee Rights document and enter into employee_rights field
            frappe.model.with_doc('Employee Rights', frm.doc.applied_rights, function() {
                let doc = frappe.get_doc('Employee Rights', frm.doc.applied_rights);
                frm.clear_table('employee_rights');
                $.each(doc.applicable_rights, function(_, row) {
                    let child = frm.add_child('employee_rights');
                    child.individual_right = row.individual_right;
                });
                frm.refresh_field('employee_rights');
            });
        }
    }
});