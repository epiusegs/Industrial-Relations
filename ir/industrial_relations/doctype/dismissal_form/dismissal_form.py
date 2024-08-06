# Copyright (c) 2024, BuFf0k and contributors
# For license information, please see license.txt

import frappe
from frappe.model.mapper import get_mapped_doc
from frappe.model.document import Document


class DismissalForm(Document):
	pass

@frappe.whitelist()
def make_dismissal_form(source_name, target_doc=None):
    from frappe.model.mapper import get_mapped_doc

    def set_missing_values(source, target):
        target.linked_disciplinary_action = source_name

    doclist = get_mapped_doc("Disciplinary Action", source_name, {
        "Disciplinary Action": {
            "doctype": "Dismissal Form",
            "field_map": {
                "name": "linked_disciplinary_action"
            }
        }
    }, target_doc, set_missing_values)

    return doclist

@frappe.whitelist()
def fetch_disciplinary_action_data(disciplinary_action):
    data = frappe.db.get_value('Disciplinary Action', disciplinary_action, 
        ['accused', 'accused_name', 'accused_coy', 'accused_pos', 'company'], as_dict=True)

    if not data:
        return {}
    
    # Fetch child table data
    disciplinary_action_doc = frappe.get_doc('Disciplinary Action', disciplinary_action)
    
    previous_disciplinary_outcomes = [
        {
            'disc_action': row.disc_action,
            'date': row.date,
            'sanction': row.sanction,
            'charges': row.charges
        } for row in disciplinary_action_doc.previous_disciplinary_outcomes
    ]
    
    final_charges = [
        {
            'indiv_charge': f"({row.code_item}) {row.charge}"
        } for row in disciplinary_action_doc.final_charges
    ]
    
    data.update({
        'previous_disciplinary_outcomes': previous_disciplinary_outcomes,
        'final_charges': final_charges
    })
    
    return data

@frappe.whitelist()
def fetch_company_letter_head(company):
    letter_head = frappe.db.get_value('Company', company, 'default_letter_head')
    return {'letter_head': letter_head} if letter_head else {}