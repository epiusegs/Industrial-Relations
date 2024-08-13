# Copyright (c) 2024, BuFf0k and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
    columns, data = [], []
    
    # Define the columns
    columns = [
        {"fieldname": "name", "label": "Document Name", "fieldtype": "Link", "options": "Disciplinary Offence", "width": 150},
        {"fieldname": "offence_description", "label": "Offence Description and Notes", "fieldtype": "Data", "width": 300},
        {"fieldname": "sanction_on_first_offence", "label": "First Offence Sanction", "fieldtype": "Data", "width": 150},
        {"fieldname": "sanction_on_second_offence", "label": "Second Offence Sanction", "fieldtype": "Data", "width": 150},
        {"fieldname": "sanction_on_third_offence", "label": "Third Offence Sanction", "fieldtype": "Data", "width": 150},
        {"fieldname": "sanction_on_fourth_offence", "label": "Fourth Offence Sanction", "fieldtype": "Data", "width": 150}
    ]

    # Fetch all Disciplinary Offence records
    offences = frappe.get_all(
        "Disciplinary Offence", 
        fields=["name", "category_of_offence", "offence_description", "notes", 
                "sanction_on_first_offence", "sanction_on_second_offence", 
                "sanction_on_third_offence", "sanction_on_fourth_offence"],
        order_by="category_of_offence, name"
    )
    
    current_category = None
    for offence in offences:
        # Fetch the disc_cat_desc from the linked "Offence Category" doctype
        if offence.category_of_offence != current_category:
            category_desc = frappe.get_value("Offence Category", offence.category_of_offence, "disc_cat_desc")
            # Add a heading row for the new category
            data.append({
                "name": "<b>{}</b>".format(category_desc),
                "offence_description": "",
                "sanction_on_first_offence": "",
                "sanction_on_second_offence": "",
                "sanction_on_third_offence": "",
                "sanction_on_fourth_offence": ""
            })
            current_category = offence.category_of_offence
        
        # Fetch the disc_offence_out from the linked Offence Outcome doctype for each sanction
        first_offence_outcome = frappe.get_value("Offence Outcome", offence.sanction_on_first_offence, "disc_offence_out") if offence.sanction_on_first_offence else ""
        second_offence_outcome = frappe.get_value("Offence Outcome", offence.sanction_on_second_offence, "disc_offence_out") if offence.sanction_on_second_offence else ""
        third_offence_outcome = frappe.get_value("Offence Outcome", offence.sanction_on_third_offence, "disc_offence_out") if offence.sanction_on_third_offence else ""
        fourth_offence_outcome = frappe.get_value("Offence Outcome", offence.sanction_on_fourth_offence, "disc_offence_out") if offence.sanction_on_fourth_offence else ""
        
        # Add the offence row with the additional details
        data.append({
            "name": offence.name,
            "offence_description": "{}<br><i>{}</i>".format(offence.offence_description, offence.notes),
            "sanction_on_first_offence": "{}<br><i>{}</i>".format(offence.sanction_on_first_offence, first_offence_outcome),
            "sanction_on_second_offence": "{}<br><i>{}</i>".format(offence.sanction_on_second_offence, second_offence_outcome),
            "sanction_on_third_offence": "{}<br><i>{}</i>".format(offence.sanction_on_third_offence, third_offence_outcome),
            "sanction_on_fourth_offence": "{}<br><i>{}</i>".format(offence.sanction_on_fourth_offence, fourth_offence_outcome)
        })

    return columns, data
