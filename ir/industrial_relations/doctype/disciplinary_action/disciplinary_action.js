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
        //Fetch disciplinary actions with the same accused
        if (frm.doc.accused) {
            frappe.call({
                method: 'frappe.client.get_list',
                args: {
                    doctype: 'Disciplinary Action',
                    filters: {
                        accused: frm.doc.accused,
                        name: ['!=', frm.doc.name]  // Exclude the current document
                    },
                    fields: ['name', 'outcome_date', 'outcome']
                },
                callback: function(r) {
                    if (r.message) {
                        // Clear existing child table entries
                        frm.clear_table('previous_disciplinary_outcomes');
                        // Populate the child table with fetched data
                        r.message.forEach(function(row) {
                            let child = frm.add_child('previous_disciplinary_outcomes');
                            child.disc_action = row.name;
                            child.date = row.outcome_date;
                            child.sanction = row.outcome;
                        });
                        // Refresh the form to show the updated child table
                        frm.refresh_field('previous_disciplinary_outcomes');
                    }
                }
            });
        }
    }
});
frappe.ui.form.on('Disciplinary Action', {
    complainant: function(frm) {
        //Fetch employee_name field from Employee document and enter into compl_name field
        if (frm.doc.complainant) {
            frappe.db.get_value('Employee', frm.doc.complainant, 'employee_name', (e) => {
                if (e && e.employee_name) {
                    frm.set_value('compl_name', e.employee_name);
                } else {
                    frm.set_value('compl_name', '');
                }
            });
        }
        //Fetch designation field from Employee document and enter into compl_pos field
        if (frm.doc.complainant) {
            frappe.db.get_value('Employee', frm.doc.complainant, 'designation', (f) => {
                if (f && f.designation) {
                    frm.set_value('compl_pos', f.designation);
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
            frappe.db.get_value('Company', frm.doc.company, 'default_letter_head', (g) => {
               if (g && g.default_letter_head) {
                    frm.set_value('letter_head', g.default_letter_head);
                } else {
                    frm.set_value('letter_head', '');
                }
            });
        }
}});