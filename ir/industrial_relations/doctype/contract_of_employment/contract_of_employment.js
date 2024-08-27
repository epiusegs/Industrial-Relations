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
    },

    working_hours: function(frm) {
        if (frm.doc.working_hours) {
            frappe.db.get_doc('Contract Section', frm.doc.working_hours).then(doc => {
                frm.set_value('has_hours', doc.has_hours || 0);
            });
        }
    },

    remuneration: function(frm) {
        if (frm.doc.remuneration) {
            frappe.db.get_doc('Contract Section', frm.doc.remuneration).then(doc => {
                frm.set_value('has_allowances', doc.has_allowances || 0);
            });
        }
    },

    has_hours: function(frm) {
        frm.events.toggle_working_hours_section(frm);
    },

    has_retirement: function(frm) {
        frm.events.toggle_retirement_fields(frm);
    },

    has_expiry: function(frm) {
        frm.events.toggle_expiry_fields(frm);
    },

    toggle_working_hours_section: function(frm) {
        let should_display = frm.doc.has_hours ? 1 : 0;
        frm.toggle_display('monday_section', should_display);
    },

    toggle_retirement_fields: function(frm) {
        let should_display = frm.doc.has_retirement ? 1 : 0;
        frm.toggle_display('retirement_age', should_display);
    },

    toggle_expiry_fields: function(frm) {
        let should_display = frm.doc.has_expiry ? 1 : 0;
        frm.toggle_display('end_date', should_display);
        frm.toggle_display('project', should_display);
    }
});

