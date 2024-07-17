// Copyright (c) 2024, BuFf0k and contributors
// For license information, please see license.txt

frappe.ui.form.on('Warning Form', {
    linked_disciplinary_action: function(frm, cdt, cdn) {
        //Fetch accused field from Disciplinary Action document and enter into name field
        if (frm.doc.linked_disciplinary_action) {
            frappe.db.get_value('Disciplinary Action', frm.doc.linked_disciplinary_action, 'accused', (a) => {
                if (a && a.accused) {
                    frm.set_value('employee', a.accused);
                } else {
                    frm.set_value('employee', '');
                }
            });
        }
        //Fetch data from the previous_disciplinary_outcomes field in the Disciplinary Action document and enter into the disciplinary_history field
        if (frm.doc.linked_disciplinary_action) {
            frappe.model.with_doc("Disciplinary Action", frm.doc.linked_disciplinary_action, function() {
                var b = frappe.model.get_doc("Disciplinary Action", frm.doc.linked_disciplinary_action);
                cur_frm.clear_table("disciplinary_history");
                $.each(b.previous_disciplinary_outcomes, function(c, d) {
                    c = frm.add_child("disciplinary_history");
                    c.disc_action = d.disc_action;
                    c.date = d.date;
                    c.sanction = d.sanction;
                    c.charges = d.charges;
                });
                cur_frm.refresh_field("disciplinary_history");
            });
        }
        //Fetch data from the final_charges field in the Disciplinary Action document and enter into the warning_charges field
        if (frm.doc.linked_disciplinary_action) {
            frappe.model.with_doc("Disciplinary Action", frm.doc.linked_disciplinary_action, function() {
                var e = frappe.model.get_doc("Disciplinary Action", frm.doc.linked_disciplinary_action);
                cur_frm.clear_table("warning_charges");
                $.each(e.final_charges, function(_, f) {
                    var g = frm.add_child("warning_charges");
                    g.warning_charge = `(${f.code_item}) ${f.charge}`;
                    
                });
                cur_frm.refresh_field("warning_charges");
            });
}

}});
frappe.ui.form.on('Warning Form', {
    employee: function(frm) {
        //Fetch employee_name field from Employee document and enter into names field
        if (frm.doc.employee) {
            frappe.db.get_value('Employee', frm.doc.employee, 'employee_name', (h) => {
                if (h && h.employee_name) {
                    frm.set_value('names', h.employee_name);
                } else {
                    frm.set_value('names', '');
                }
            });
        }
        //Fetch employee field from Employee document and enter into coy field
        if (frm.doc.employee) {
            frappe.db.get_value('Employee', frm.doc.employee, 'employee', (i) => {
                if (i && i.employee) {
                    frm.set_value('coy', i.employee);
                } else {
                    frm.set_value('coy', '');
                }
            });
        }
        //Fetch designation field from Employee document and enter into position field
        if (frm.doc.employee) {
            frappe.db.get_value('Employee', frm.doc.employee, 'designation', (j) => {
                if (j && j.designation) {
                    frm.set_value('position', j.designation);
                } else {
                    frm.set_value('position', '');
                }
            });
        }
        //Fetch company field from the Employee document and enter into company field
        if (frm.doc.employee) {
            frappe.db.get_value('Employee', frm.doc.employee, 'company', (k) => {
                if (k && k.company) {
                    frm.set_value('company', k.company);
                } else {
                    frm.set_value('company', '');
                }
            });
        }
    }
});
frappe.ui.form.on('Warning Form', {
    company: function(frm) {
        //Fetch default_letter_head field from the Company document and enter into the letter_head field
        if (frm.doc.company) {
            frappe.db.get_value('Company', frm.doc.company, 'default_letter_head', (l) => {
               if (l && l.default_letter_head) {
                    frm.set_value('letter_head', l.default_letter_head);
                } else {
                    frm.set_value('letter_head', '');
                }
            });
        }
}});