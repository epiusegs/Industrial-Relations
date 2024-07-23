# Copyright (c) 2024, BuFf0k and contributors
# For license information, please see license.txt

import frappe
from frappe.model.mapper import get_mapped_doc
from frappe.model.document import Document


class NotGuiltyForm(Document):
	pass

@frappe.whitelist()
def make_not_guilty_form(source_name, target_doc=None):
    from frappe.model.mapper import get_mapped_doc

    def set_missing_values(source, target):
        target.linked_disciplinary_action = source_name

    doclist = get_mapped_doc("Disciplinary Action", source_name, {
        "Disciplinary Action": {
            "doctype": "Not Guilty Form",
            "field_map": {
                "name": "linked_disciplinary_action"
            }
        }
    }, target_doc, set_missing_values)

    return doclist