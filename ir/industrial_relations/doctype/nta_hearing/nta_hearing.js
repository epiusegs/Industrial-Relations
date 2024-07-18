// Copyright (c) 2024, BuFf0k and contributors
// For license information, please see license.txt

frappe.ui.form.on('NTA Hearing', {
    refresh: function(frm) {
        // Manually trigger the linked_disciplinary_action handler if the field is already set
        if (frm.doc.linked_disciplinary_action) {
            frm.trigger('linked_disciplinary_action');
        }
    },
    
    linked_disciplinary_action: function(frm) {
        if (frm.doc.linked_disciplinary_action) {
            // Fetch accused field from Disciplinary Action document and enter into employee field
            frappe.db.get_value('Disciplinary Action', frm.doc.linked_disciplinary_action, 'accused', (r) => {
                frm.set_value('employee', r ? r.accused : '');
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

                // Fetch data from final_charges and enter into nta_charges field
                frm.clear_table('nta_charges');
                $.each(doc.final_charges, function(_, row) {
                    let child = frm.add_child('nta_charges');
                    child.nta_charge = `(${row.code_item}) ${row.charge}`;
                });
                frm.refresh_field('nta_charges');
            });
        }
    },

    employee: function(frm) {
        if (frm.doc.employee) {
            // Fetch employee_name field from Employee document and enter into names field
            frappe.db.get_value('Employee', frm.doc.employee, 'employee_name', (r) => {
                frm.set_value('names', r ? r.employee_name : '');
            });

            // Fetch employee field from Employee document and enter into coy field
            frappe.db.get_value('Employee', frm.doc.employee, 'employee', (r) => {
                frm.set_value('coy', r ? r.employee : '');
            });

            // Fetch designation field from Employee document and enter into position field
            frappe.db.get_value('Employee', frm.doc.employee, 'designation', (r) => {
                frm.set_value('position', r ? r.designation : '');
            });

            // Fetch company field from Employee document and enter into company field
            frappe.db.get_value('Employee', frm.doc.employee, 'company', (r) => {
                frm.set_value('company', r ? r.company : '');
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
    }
});