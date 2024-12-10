// Copyright (c) 2024, BuFf0k and contributors
// For license information, please see license.txt

frappe.ui.form.on("Managerial Instructions", {
    company: function(frm) {
        if (frm.doc.company) {
            frappe.call({
                method: 'ir.industrial_relations.doctype.managerial_instructions.managerial_instructions.fetch_company_letter_head',
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

    employee: function(frm) {
        if (frm.doc.employee) {
            frappe.call({
                method: 'ir.industrial_relations.doctype.managerial_instructions.managerial_instructions.fetch_employee_name',
                args: {
                    employee: frm.doc.employee
                },
                callback: function(r) {
                    if (r.message) {
                        frm.doc.employee_name = r.message.employee_name || '';
                        frm.refresh_field('employee_name');
                    }
                }
            });
        }
    }

});