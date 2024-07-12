// Copyright (c) 2024, BuFf0k and contributors
// For license information, please see license.txt
frappe.ui.form.on('Disciplinary Action', {
    accused: function(frm) {
        if (frm.doc.accused) {
            frappe.db.get_value('Employee', frm.doc.accused, 'employee_name', (a) => {
                if (a && a.employee_name) {
                    frm.set_value('accused_name', a.employee_name);
                } else {
                    frm.set_value('accused_name', '');
                }
            });
        } else {
            frm.set_value('accused_name', '');
        }
        if (frm.doc.accused) {
            frappe.db.get_value('Employee', frm.doc.accused, 'employee', (b) => {
                if (b && b.employee) {
                    frm.set_value('accused_coy', b.employee);
                } else {
                    frm.set_value('accused_coy', '');
                }
            });
        } else {
            frm.set_value('accused_coy', '');
        }
        if (frm.doc.accused) {
            frappe.db.get_value('Employee', frm.doc.accused, 'designation', (c) => {
                if (c && c.designation) {
                    frm.set_value('accused_pos', c.designation);
                } else {
                    frm.set_value('accused_pos', '');
                }
            });
        } else {
            frm.set_value('accused_pos', '');
        }
    }
});

frappe.ui.form.on('Disciplinary Action', {
    complainant: function(frm) {
        if (frm.doc.complainant) {
            frappe.db.get_value('Employee', frm.doc.complainant, 'employee_name', (d) => {
                if (d && d.employee_name) {
                    frm.set_value('compl_name', d.employee_name);
                } else {
                    frm.set_value('compl_name', '');
                }
            });
        } else {
            frm.set_value('compl_name', '');
        }
        if (frm.doc.complainant) {
            frappe.db.get_value('Employee', frm.doc.complainant, 'designation', (e) => {
                if (e && e.designation) {
                    frm.set_value('compl_pos', e.designation);
                } else {
                    frm.set_value('compl_pos', '');
                }
            });
        } else {
            frm.set_value('compl_pos', '');
        }
    }
});
