// Copyright (c) 2024, BuFf0k and contributors
// For license information, please see license.txt
frappe.ui.form.on('Disciplinary Action', {
    accused: function(frm) {
        //Fetch employee_name field from Employee document and enter into accused_name field
        if (frm.doc.accused) {
            frappe.db.get_value('Employee', frm.doc.accused, 'employee_name', (a) => {
                if (a && a.employee_name) {
                    frm.set_value('accused_name', a.employee_name);
                } else {
                    frm.set_value('accused_name', '');
                }
            });
        }
        //Fetch employee field from Employee document and enter into accused_coy field
        if (frm.doc.accused) {
            frappe.db.get_value('Employee', frm.doc.accused, 'employee', (b) => {
                if (b && b.employee) {
                    frm.set_value('accused_coy', b.employee);
                } else {
                    frm.set_value('accused_coy', '');
                }
            });
        }
        //Fetch designation field from Employee document and enter into accused_pos field 
        if (frm.doc.accused) {
            frappe.db.get_value('Employee', frm.doc.accused, 'designation', (c) => {
                if (c && c.designation) {
                    frm.set_value('accused_pos', c.designation);
                } else {
                    frm.set_value('accused_pos', '');
                }
            });
        }
        //Fetch company field from the Employee document and enter into company field
        if (frm.doc.accused) {
            frappe.db.get_value('Employee', frm.doc.accused, 'company', (d) => {
                if (d && d.company) {
                    frm.set_value('company', d.company);
                } else {
                    frm.set_value('company', '');
                }
            });
        }
        //Fetch data and completes the disciplinary_history child table based on accused previous disciplinary actions
        if (frm.doc.accused) {
            frappe.call({
                method: 'frappe.client.get_list',
                args: {
                    doctype: 'Disciplinary Action',
                    filters: {
                        accused: frm.doc.accused,
                        outcome: ['!=',''], //Exclude documents without outcomes
                        name: ['!=', frm.doc.name]  // Exclude the current document
                    },
                    fields: ['name', 'outcome_date', 'outcome']
                },
                callback: function(e) {
                    if (e.message) {
                        // Clear existing child table entries
                        frm.clear_table('previous_disciplinary_outcomes');
                        let action_count = e.message.length;
                        let completed_actions = 0;
                        e.message.forEach(function(row) {
                            frappe.model.with_doc('Disciplinary Action', row.name, function() {
                                let action_doc = frappe.get_doc('Disciplinary Action', row.name);
                                let charges = [];
                                action_doc.final_charges.forEach(function(charge_row) {
                                    charges.push(`(${charge_row.code_item}) ${charge_row.charge}`);
                                });
                                // Add the row to previous_disciplinary_outcomes
                                let child = frm.add_child('previous_disciplinary_outcomes');
                                child.disc_action = action_doc.name;
                                child.date = action_doc.outcome_date;
                                child.sanction = action_doc.outcome;
                                child.charges = charges.join('\n');  // Each charge on a new line
                                completed_actions++;
                                // Refresh the form to show the updated child table when all calls are completed
                                if (completed_actions === action_count) {
                                    frm.refresh_field('previous_disciplinary_outcomes');
                                }
                            });
                        });
                    }
                }
            });
        }
        //frm.add_custom_button(__('Create Warning Form'), function() {
            // Create a new Written Warning document
        //    frappe.new_doc('Warning Form', {
        //        linked_disciplinary_action: frm.doc.name  // Automatically link to the Disciplinary Action document
        //    });
        //});
    }
});
frappe.ui.form.on('Disciplinary Action', {
    complainant: function(frm) {
        //Fetch employee_name field from Employee document and enter into compl_name field
        if (frm.doc.complainant) {
            frappe.db.get_value('Employee', frm.doc.complainant, 'employee_name', (f) => {
                if (f && f.employee_name) {
                    frm.set_value('compl_name', f.employee_name);
                } else {
                    frm.set_value('compl_name', '');
                }
            });
        }
        //Fetch designation field from Employee document and enter into compl_pos field
        if (frm.doc.complainant) {
            frappe.db.get_value('Employee', frm.doc.complainant, 'designation', (g) => {
                if (g && g.designation) {
                    frm.set_value('compl_pos', g.designation);
                } else {
                    frm.set_value('compl_pos', '');
                }
            });
        }
}});
frappe.ui.form.on('Disciplinary Action', {
    company: function(frm) {
        //Fetch default_letter_head field from the Company document and enter into the letter_head field
        if (frm.doc.company) {
            frappe.db.get_value('Company', frm.doc.company, 'default_letter_head', (h) => {
               if (h && h.default_letter_head) {
                    frm.set_value('letter_head', h.default_letter_head);
                } else {
                    frm.set_value('letter_head', '');
                }
            });
        }
}});