# Copyright (c) 2024, BuFf0k and contributors
# For license information, please see license.txt

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
        frm.toggle_display(['make_warning_form', 'make_nta_hearing', 'write_disciplinary_outcome_report'], frm.doc.docstatus === 0 && !frm.doc.__islocal && frm.doc.workflow_state !== 'Submitted');

        if (frappe.user.has_role("IR Manager")) {
            frm.add_custom_button(__('Issue NTA'), function() {
                make_nta_hearing(frm);
            }).addClass('btn-primary').attr('id', 'make_nta_hearing');
        	
        	frm.add_custom_button(__('Write Outcome Report'), function() {
                write_disciplinary_outcome_report(frm);
            }).addClass('btn-primary').attr('id', 'write_disciplinary_outcome_report');
        
        	frm.add_custom_button(__('Issue Not Guilty'), function() {
                issue_not_guilty_form(frm);
            }).addClass('btn-primary').attr('id', 'issue_not_guilty_form');
        
        	frm.add_custom_button(__('Issue Warning'), function() {
                make_warning_form(frm);
            }).addClass('btn-primary').attr('id', 'make_warning_form');
            
        	frm.add_custom_button(__('Issue Suspension'), function() {
                issue_suspension_form(frm);
            }).addClass('btn-primary').attr('id', 'issue_suspension_form');
        
        	frm.add_custom_button(__('Issue Demotion'), function() {
                issue_demotion_form(frm);
            }).addClass('btn-primary').attr('id', 'issue_demotion_form');
        
        	frm.add_custom_button(__('Issue Pay Deduction'), function() {
                issue_pay_deduction_form(frm);
            }).addClass('btn-primary').attr('id', 'issue_pay_deduction_form');
        
        	frm.add_custom_button(__('Issue Dismissal'), function() {
                issue_dismissal_form(frm);
            }).addClass('btn-primary').attr('id', 'issue_dismissal_form');
        }

        // Fetch linked documents on refresh
        fetch_linked_documents(frm);
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

function write_disciplinary_outcome_report(frm) {
    frappe.model.open_mapped_doc({
        method: "ir.industrial_relations.doctype.disciplinary_outcome_report.disciplinary_outcome_report.write_disciplinary_outcome_report",
        frm: frm,
        args: {
            linked_disciplinary_action: frm.doc.name
        },
        freeze_message: __("Creating Disciplinary Outcome Report ...")
    });
}

function issue_not_guilty_form(frm) {
    frappe.model.open_mapped_doc({
        method: "ir.industrial_relations.doctype.not_guilty_form.not_guilty_form.make_not_guilty_form",
        frm: frm,
        args: {
            linked_disciplinary_action: frm.doc.name
        },
        freeze_message: __("Creating Not Guilty Form ...")
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

function issue_suspension_form(frm) {
    frappe.model.open_mapped_doc({
        method: "ir.industrial_relations.doctype.suspension_form.suspension_form.make_suspension_form",
        frm: frm,
        args: {
            linked_disciplinary_action: frm.doc.name
        },
        freeze_message: __("Creating Suspension Form ...")
    });
}

function issue_demotion_form(frm) {
    frappe.model.open_mapped_doc({
        method: "ir.industrial_relations.doctype.demotion_form.demotion_form.make_demotion_form",
        frm: frm,
        args: {
            linked_disciplinary_action: frm.doc.name
        },
        freeze_message: __("Creating Demotion Form ...")
    });
}

function issue_pay_deduction_form(frm) {
    frappe.model.open_mapped_doc({
        method: "ir.industrial_relations.doctype.pay_deduction_form.pay_deduction_form.make_pay_deduction_form",
        frm: frm,
        args: {
            linked_disciplinary_action: frm.doc.name
        },
        freeze_message: __("Creating Pay Deduction Form ...")
    });
}

function issue_dismissal_form(frm) {
    frappe.model.open_mapped_doc({
        method: "ir.industrial_relations.doctype.dismissal_form.dismissal_form.make_dismissal_form",
        frm: frm,
        args: {
            linked_disciplinary_action: frm.doc.name
        },
        freeze_message: __("Creating Dismissal Form ...")
    });
}

function fetch_linked_documents(frm) {
    const linked_docs = {
        "NTA Hearing": "linked_nta",
        "Disciplinary Outcome Report": "linked_outcome",
        "Warning Form": "linked_sanction",
        "Dismissal Form": "linked_sanction",
        "Demotion Form": "linked_sanction",
        "Pay Deduction Form": "linked_sanction",
        "Not Guilty Form": "linked_sanction",
        "Suspension Form": "linked_sanction"
    };

    Object.keys(linked_docs).forEach(doctype => {
        frappe.call({
            method: 'frappe.client.get_list',
            args: {
                doctype: doctype,
                filters: {
                    linked_disciplinary_action: frm.doc.name
                },
                fields: ['name']
            },
            callback: function(res) {
                if (res.message && res.message.length > 0) {
                    frm.set_value(linked_docs[doctype], res.message.map(doc => doc.name).join(', '));
                }
            }
        });
    });
}