# Copyright (c) 2024, BuFf0k and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
    columns, data = [], []
    columns = [
        {"fieldname": "name", "label": "Document Name", "fieldtype": "Link", "options": "Disciplinary Offence", "width": 150},
        {"fieldname": "offence_description", "label": "Offence Description and Notes", "fieldtype": "Data", "width": 300},
        {"fieldname": "sanction_on_first_offence", "label": "First Offence Sanction", "fieldtype": "Data", "width": 150},
        {"fieldname": "sanction_on_second_offence", "label": "Second Offence Sanction", "fieldtype": "Data", "width": 150},
        {"fieldname": "sanction_on_third_offence", "label": "Third Offence Sanction", "fieldtype": "Data", "width": 150},
        {"fieldname": "sanction_on_fourth_offence", "label": "Fourth Offence Sanction", "fieldtype": "Data", "width": 150}
    ]

    # Fetch all the Disciplinary Offence records
    offences = frappe.get_all(
        "Disciplinary Offence", 
        fields=["name", "category_of_offence", "offence_description", "notes", 
                "sanction_on_first_offence", "sanction_on_second_offence", 
                "sanction_on_third_offence", "sanction_on_fourth_offence"],
        order_by="category_of_offence, name"
    )
    
    current_category = None
    for offence in offences:
        if offence.category_of_offence != current_category:
            # Add a heading row for the new category
            data.append({
                "name": "<b>{}</b>".format(offence.category_of_offence),
                "offence_description": "",
                "sanction_on_first_offence": "",
                "sanction_on_second_offence": "",
                "sanction_on_third_offence": "",
                "sanction_on_fourth_offence": ""
            })
            current_category = offence.category_of_offence
        
        # Add the offence row
        data.append({
            "name": offence.name,
            "offence_description": "{}<br><i>{}</i>".format(offence.offence_description, offence.notes),
            "sanction_on_first_offence": offence.sanction_on_first_offence,
            "sanction_on_second_offence": offence.sanction_on_second_offence,
            "sanction_on_third_offence": offence.sanction_on_third_offence,
            "sanction_on_fourth_offence": offence.sanction_on_fourth_offence
        })

    return columns, data
