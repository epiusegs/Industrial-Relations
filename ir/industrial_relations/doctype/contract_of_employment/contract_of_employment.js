// Copyright (c) 2024, BuFf0k and contributors
// For license information, please see license.txt

frappe.ui.form.on('Contract of Employment', {
    employee: function(frm) {
        if (frm.doc.employee) {
            frappe.db.get_doc('Employee', frm.doc.employee).then(doc => {
                frm.set_value('employee_name', doc.employee_name || '');
                frm.set_value('date_of_birth', doc.date_of_birth || '');
                frm.set_value('date_of_joining', doc.date_of_joining || '');
                frm.set_value('company', doc.company || '');
                frm.set_value('designation', doc.designation || '');
                frm.set_value('current_address', doc.current_address || '');
                frm.set_value('custom_id_number', doc.custom_id_number || '');
                frm.set_value('branch', doc.branch || '');

                // Fetch default letter head
                if (doc.company) {
                    frappe.db.get_value('Company', doc.company, 'default_letter_head', (r) => {
                        frm.set_value('letter_head', r.default_letter_head || '');
                    });
                }
            });
        }
    },

    contract_type: function(frm) {
        if (frm.doc.contract_type) {
            frappe.model.with_doc('Contract Type', frm.doc.contract_type, function() {
                let contract_type_doc = frappe.get_doc('Contract Type', frm.doc.contract_type);

                // Update fields in Contract of Employment
                frm.set_value('has_expiry', contract_type_doc.has_expiry || 0);
                frm.set_value('has_retirement', contract_type_doc.has_retirement || 0);
                frm.set_value('retirement_age', contract_type_doc.retirement_age || '');

                // Clear contract_clauses table
                frm.clear_table('contract_clauses');

                // Populate contract_clauses table based on contract_terms in Contract Type
                contract_type_doc.contract_terms.forEach(term_row => {
                    frappe.model.with_doc('Contract Section', term_row.section, function() {
                        let section_doc = frappe.get_doc('Contract Section', term_row.section);

                        let clause_content = `<b>${section_doc.sec_head}</b><br>`;
                        section_doc.sec_par.forEach(paragraph => {
                            clause_content += `${paragraph.par_num}. ${paragraph.par_text}<br>`;
                        });

                        let row = frm.add_child('contract_clauses');
                        row.section_number = term_row.sec_no;
                        row.clause_content = clause_content;

                        frm.refresh_field('contract_clauses');
                    });
                });

                // Handle has_retirement logic
                if (contract_type_doc.has_retirement) {
                    let retirement_age = contract_type_doc.retirement_age;
                    let notification_date = frappe.datetime.add_months(frappe.datetime.add_years(frm.doc.date_of_birth, retirement_age), -1);
                    // Add notification logic here if needed
                }

                // Handle has_expiry logic
                if (contract_type_doc.has_expiry) {
                    frm.set_df_property('end_date', 'reqd', 1);
                    frm.set_df_property('project', 'reqd', 1);
                } else {
                    frm.set_df_property('end_date', 'reqd', 0);
                    frm.set_df_property('project', 'reqd', 0);
                }
            });
        }
    }
});

