# Copyright (c) 2024, BuFf0k and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import formatdate
from bs4 import BeautifulSoup
import re

class DisciplinaryOutcomeReport(Document):
    pass

@frappe.whitelist()
def write_disciplinary_outcome_report(source_name, target_doc=None):
    from frappe.model.mapper import get_mapped_doc

    def set_missing_values(source, target):
        target.linked_disciplinary_action = source_name

    doclist = get_mapped_doc("Disciplinary Action", source_name, {
        "Disciplinary Action": {
            "doctype": "Disciplinary Outcome Report",
            "field_map": {
                "name": "linked_disciplinary_action"
            }
        }
    }, target_doc, set_missing_values)

    return doclist

@frappe.whitelist()
def fetch_disciplinary_action_data(disciplinary_action):
    data = frappe.db.get_value('Disciplinary Action', disciplinary_action, 
        ['accused', 'accused_name', 'accused_coy', 'accused_pos', 'company', 'linked_nta'], as_dict=True)

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

@frappe.whitelist()
def fetch_linked_fields(linked_nta, linked_disciplinary_action):
    chairperson = None
    complainant = None

    if linked_nta:
        chairperson = frappe.db.get_value('NTA Hearing', linked_nta, 'chairperson')

    if linked_disciplinary_action:
        complainant = frappe.db.get_value('Disciplinary Action', linked_disciplinary_action, 'complainant')

    return {
        'chairperson': chairperson,
        'complainant': complainant,
    }

@frappe.whitelist()
def fetch_employee_names(chairperson=None, complainant=None):
    chairperson_name = None
    complainant_name = None

    if chairperson:
        chairperson_name = frappe.db.get_value('Employee', chairperson, 'employee_name')

    if complainant:
        complainant_name = frappe.db.get_value('Employee', complainant, 'employee_name')

    return {
        'chairperson_name': chairperson_name,
        'complainant_name': complainant_name,
    }

@frappe.whitelist()
def generate_numbered_html(content, paragraph_counter):
    """Generates numbered HTML content based on Quill's Delta format."""
    numbered_content = ""
    
    for item in content:
        if item.get("insert"):
            text = item["insert"].strip()
            if not text:  # Skip empty lines
                continue
            
            # Handle headings
            if "attributes" in item and "header" in item["attributes"]:
                header_level = item["attributes"]["header"]
                numbered_content += f"<h{header_level}>{text}</h{header_level}>"
            else:
                # Number paragraphs
                paragraph_counter += 1
                numbered_content += f"<p>{paragraph_counter}. {text}</p>"
    
    return numbered_content, paragraph_counter

@frappe.whitelist()
def compile_outcome(docname):
    doc = frappe.get_doc("Disciplinary Outcome Report", docname)

    # Fetch the linked NTA document's venue
    venue = ""
    if doc.linked_nta:
        linked_nta_doc = frappe.get_doc("NTA Hearing", doc.linked_nta)
        venue = linked_nta_doc.venue or "Unknown Venue"

    # Helper to convert a date to words
    def date_to_words(date_str):
        return frappe.utils.formatdate(date_str, "d MMMM yyyy")

    date_in_words = date_to_words(doc.date) if doc.date else "Unknown Date"

    # Start compiling the outcome
    outcome_content = f"""
        <h1 style="text-align:center;">OUTCOME OF A DISCIPLINARY ENQUIRY</h1>
        <h3>Held at {venue}, on the {date_in_words}, with:</h3>
        <p>Chairperson: {doc.chairperson_name or 'Unknown'}</p>
        <p>Complainant: {doc.complainant_name or 'Unknown'}</p>
        <p>Accused Employee: {doc.names or 'Unknown'} ({doc.coy or 'Unknown'})</p>
    """

    # Process sections with continuous numbering
    sections = [
        ("Introduction", doc.introduction),
        ("Complainant's Statement of Case", doc.complainant_case),
        ("Accused Employee's Statement of Case", doc.accused_case),
        ("Analysis of Evidence", doc.analysis_of_evidence),
        ("Finding", doc.finding),
        ("Mitigating Considerations", doc.mitigating_considerations),
        ("Aggravating Considerations", doc.aggravating_conisderations),  # Intentional typo
        ("Outcome", doc.outcome),
    ]

    paragraph_counter = 1  # Start numbering from 1
    for title, content in sections:
        if content:
            # Add section heading
            outcome_content += f"<h3>{title}</h3>"
            # Generate numbered content for the section
            numbered_html, paragraph_counter = generate_numbered_html(content, paragraph_counter)
            outcome_content += numbered_html

    # Save to the complete_outcome field
    doc.complete_outcome = outcome_content
    doc.save()

    return {"success": True}
