// Copyright (c) 2024, BuFf0k and contributors
// For license information, please see license.txt

frappe.ui.form.on('Contract of Employment', {
    employee: function(frm) {
        if (frm.doc.employee) {
            frappe.call({
                method: 'frappe.client.get',
                args: {
                    doctype: 'Employee',
                    name: frm.doc.employee
                },
                callback: function(r) {
                    if (r.message) {
                        frm.set_value('employee_name', r.message.employee_name);
                        frm.set_value('date_of_birth', r.message.date_of_birth);
                        frm.set_value('date_of_joining', r.message.date_of_joining);
                        frm.set_value('designation', r.message.designation);
                        frm.set_value('current_address', r.message.current_address);
                        frm.set_value('custom_id_number', r.message.custom_id_number);
                        frm.set_value('branch', r.message.branch);
                        
                        // Fetch company details
                        if (r.message.company) {
                            frappe.call({
                                method: 'frappe.client.get',
                                args: {
                                    doctype: 'Company',
                                    name: r.message.company
                                },
                                callback: function(r2) {
                                    if (r2.message) {
                                        frm.set_value('company', r.message.company);
                                        frm.set_value('letter_head', r2.message.default_letter_head);
                                    }
                                }
                            });
                        }
                    }
                }
            });
        }
    },

    contract_type: function(frm) {
        if (frm.doc.contract_type) {
            frappe.call({
                method: 'frappe.client.get',
                args: {
                    doctype: 'Contract Type',
                    name: frm.doc.contract_type
                },
                callback: function(r) {
                    if (r.message) {
                        frm.set_value('has_expiry', r.message.has_expiry);
                        frm.set_value('has_retirement', r.message.has_retirement);
                        frm.set_value('retirement_age', r.message.retirement_age);
                        
                        // Clear clauses table
                        frm.clear_table('contract_clauses');
                        
                        // Populate clauses table
                        r.message.sections.forEach(section => {
                            let new_row = frm.add_child('contract_clauses');
                            new_row.section_number = section.sec_no;
                            frappe.call({
                                method: 'frappe.client.get',
                                args: {
                                    doctype: 'Contract Section',
                                    name: section.section
                                },
                                callback: function(sec) {
                                    if (sec.message) {
                                        new_row.clause_content = sec.message.sec_par.map(par => {
                                            return `<p>${par.par_num}. ${par.par_text}</p>`;
                                        }).join('');
                                    }
                                    frm.refresh_field('contract_clauses');
                                }
                            });
                        });
                    }
                }
            });
        }
    }
});
