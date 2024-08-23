# Copyright (c) 2024, BuFf0k and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ContractType(Document):
	pass

class ContractType(Document):
    def validate(self):
        self.check_required_sections()

    def check_required_sections(self):
        """Ensures that the Contract Type contains the required sections."""
        required_sections = ["Remuneration Placeholder", "Working Hours Placeholder"]
        linked_sections = [term.section for term in self.contract_terms]

        # Fetch the names of the required Contract Section documents
        missing_sections = []
        for section_name in required_sections:
            section_doc_name = frappe.db.get_value('Contract Section', {'sec_head': section_name}, 'name')
            if section_doc_name not in linked_sections:
                missing_sections.append(section_name)

        if missing_sections:
            frappe.throw(f"The following required sections are missing: {', '.join(missing_sections)}. "
                         "Please ensur that these clauses are in your template in order to ensure generatoin functionality.")

