# Copyright (c) 2024, BuFf0k and contributors
# For license information, please see license.txt

import frappe
from frappe.model.mapper import get_mapped_doc
from frappe.model.document import Document


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