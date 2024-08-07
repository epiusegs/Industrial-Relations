# Copyright (c) 2024, BuFf0k and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.model.document import Document

class DisciplinaryAction(Document):
    pass

@frappe.whitelist()
def fetch_employee_data(employee, fields):
    frappe.flags.ignore_permissions = True

    # Parse the fields argument from JSON string to dictionary
    fields = json.loads(fields)

    data = {}
    for field in fields:
        value = frappe.db.get_value('Employee', employee, field)
        data[fields[field]] = value if value else ''
    
    return data

@frappe.whitelist()
def fetch_default_letter_head(company):
    frappe.flags.ignore_permissions = True

    letter_head = frappe.db.get_value('Company', company, 'default_letter_head')
    return letter_head if letter_head else ''

@frappe.whitelist()
def fetch_disciplinary_history(accused, current_doc_name):
    frappe.flags.ignore_permissions = True

    disciplinary_actions = frappe.get_all('Disciplinary Action', filters={
        'accused': accused,
        'name': ['!=', current_doc_name]
    }, fields=['name', 'outcome_date', 'outcome'])

    history = []

    for action in disciplinary_actions:
        action_doc = frappe.get_doc('Disciplinary Action', action.name)
        charges = '\n'.join([f"({charge_row.code_item}) {charge_row.charge}" for charge_row in action_doc.final_charges])
        sanction = action_doc.outcome if action_doc.outcome else f"Pending {action_doc.name}"

        history.append({
            'disc_action': action_doc.name,
            'date': action_doc.outcome_date,
            'sanction': sanction,
            'charges': charges
        })

    return history

@frappe.whitelist()
def fetch_linked_documents(doc_name):
    frappe.flags.ignore_permissions = True

    linked_docs = {
        "Warning Form": "linked_warning",
        "Dismissal Form": "linked_dismissal",
        "Demotion Form": "linked_demotion",
        "Pay Deduction Form": "linked_pay_deduction",
        "Not Guilty Form": "linked_not_guilty",
        "Suspension Form": "linked_suspension",
        "Voluntary Seperation Agreement": "linked_vsp"
    }

    relevant_fields = {
        "linked_warning": "warning_type",
        "linked_dismissal": "dismissal_type",
        "linked_demotion": "demotion_type",
        "linked_pay_deduction": "pay_deduction_type",
        "linked_not_guilty": "type_of_not_guilty",
        "linked_suspension": "suspension_type",
        "linked_vsp": "vsp_type"
    }

    result = {
        'linked_documents': {},
        'latest_outcome': None,
        'latest_outcome_date': None
    }

    for doctype, fieldname in linked_docs.items():
        docs = frappe.get_all(doctype, filters={'linked_disciplinary_action': doc_name}, fields=['name', 'outcome_date'])

        if docs:
            result['linked_documents'][fieldname] = [doc['name'] for doc in docs]
            for doc in docs:
                doc_outcome = frappe.db.get_value(doctype, doc['name'], relevant_fields[fieldname])
                if doc_outcome:
                    doc_outcome_date = doc['outcome_date']
                    if not result['latest_outcome_date'] or doc_outcome_date > result['latest_outcome_date']:
                        result['latest_outcome_date'] = doc_outcome_date
                        result['latest_outcome'] = doc_outcome
    
    return result

@frappe.whitelist()
def fetch_additional_linked_documents(doc_name):
    frappe.flags.ignore_permissions = True

    result = {
        'linked_nta': None,
        'linked_outcome': None
    }

    nta_hearing = frappe.get_all('NTA Hearing', filters={'linked_disciplinary_action': doc_name}, fields=['name'])
    disciplinary_outcome_report = frappe.get_all('Disciplinary Outcome Report', filters={'linked_disciplinary_action': doc_name}, fields=['name'])

    if nta_hearing:
        result['linked_nta'] = nta_hearing[0]['name']
    if disciplinary_outcome_report:
        result['linked_outcome'] = disciplinary_outcome_report[0]['name']
    
    return result

@frappe.whitelist()
def fetch_complainant_data(complainant):
    frappe.flags.ignore_permissions = True

    data = {
        'compl_name': frappe.db.get_value('Employee', complainant, 'employee_name') or '',
        'compl_pos': frappe.db.get_value('Employee', complainant, 'designation') or ''
    }
    
    return data

@frappe.whitelist()
def check_if_ss(accused):
    trade_unions = frappe.get_all('Trade Union', fields=['name'])

    for tu in trade_unions:
        ss_list = frappe.get_all('Union Shop Stewards', filters={'parent': tu.name, 'parentfield': 'ss_list', 'ss_id': accused}, fields=['ss_id'])
        if ss_list:
            return {
                'is_ss': True,
                'ss_union': tu.name
            }
    return {
        'is_ss': False,
        'ss_union': None
    }