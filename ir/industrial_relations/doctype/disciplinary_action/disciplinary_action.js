// Copyright (c) 2024, BuFf0k and contributors
// For license information, please see license.txt
frappe.ui.form.on('Disciplinary Action', {
    accused: function(frm) {
        if (frm.doc.accused) {
            fetch_employee_data(frm, frm.doc.accused, {
                'employee_name': 'accused_name',
                'employee': 'accused_coy',
                'designation': 'accused_pos',
                'company': 'company'
            });
            fetch_disciplinary_history(frm, frm.doc.accused);
        }
    },

    refresh: function(frm) {
        frm.toggle_display(['make_warning_form', 'make_nta_hearing'], frm.doc.docstatus === 0 && !frm.doc.__islocal);

        if (frappe.user.has_role("IR Manager")) {
            frm.add_custom_button(__('Issue Warning'), function() {
                make_warning_form(frm);
            }).addClass('btn-primary').attr('id', 'make_warning_form');

            frm.add_custom_button(__('Issue NTA'), function() {
                make_nta_hearing(frm);
            }).addClass('btn-primary').attr('id', 'make_nta_hearing');
        }
    }
});

function fetch_employee_data(frm, employee, fields) {
    Object.keys(fields).forEach(field => {
        frappe.db.get_value('Employee', employee, field, (res) => {
            if (res && res[field]) {
                frm.set_value(fields[field], res[field]);
            } else {
                frm.set_value(fields[field], '');
            }
        });
    });
}

function fetch_disciplinary_history(frm, accused) {
    frappe.call({
        method: 'frappe.client.get_list',
        args: {
            doctype: 'Disciplinary Action',
            filters: {
                accused: accused,
                outcome: ['!=', ''], // Exclude documents without outcomes
                name: ['!=', frm.doc.name] // Exclude the current document
            },
            fields: ['name', 'outcome_date', 'outcome']
        },
        callback: function(res) {
            if (res.message) {
                frm.clear_table('previous_disciplinary_outcomes');
                res.message.forEach(function(row) {
                    frappe.model.with_doc('Disciplinary Action', row.name, function() {
                        let action_doc = frappe.get_doc('Disciplinary Action', row.name);
                        let charges = action_doc.final_charges.map(charge_row => `(${charge_row.code_item}) ${charge_row.charge}`).join('\n');
                        let child = frm.add_child('previous_disciplinary_outcomes');
                        child.disc_action = action_doc.name;
                        child.date = action_doc.outcome_date;
                        child.sanction = action_doc.outcome;
                        child.charges = charges;
                    });
                });
                frm.refresh_field('previous_disciplinary_outcomes');
            }
        }
    });
}

function make_warning_form(frm) {
    frappe.model.open_mapped_doc({
        method: "ir.industrial_relations.doctype.warning_form.warning_form.make_warning_form",
        frm: frm,
        args: {
            linked_disciplinary_action: frm.doc.name
        },
        freeze_message: __("Creating Warning Form ...")
    });
}

function make_nta_hearing(frm) {
    frappe.model.open_mapped_doc({
        method: "ir.industrial_relations.doctype.nta_hearing.nta_hearing.make_nta_hearing",
        frm: frm,
        args: {
            linked_disciplinary_action: frm.doc.name
        },
        freeze_message: __("Creating NTA Hearing ...")
    });
}