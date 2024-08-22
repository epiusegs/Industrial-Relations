# Copyright (c) 2024, BuFf0k and contributors
# For license information, please see license.txt

import frappe, re
from frappe.model.document import Document
from frappe.utils import add_months, add_years, format_time

class ContractofEmployment(Document):
    def validate(self):
        self.update_contract_clauses()
        self.generate_contract()
        self.notify_retirement()

    def update_contract_clauses(self):
        """Fetches and updates the contract clauses from the linked Contract Type."""
        if self.contract_type:
            contract_type_doc = frappe.get_doc('Contract Type', self.contract_type)
            self.contract_clauses = []

            for term in contract_type_doc.contract_terms:
                section = frappe.get_doc('Contract Section', term.section)
                
                # Numbered section header
                clause_content = f"<b>{term.sec_no}. {section.sec_head}</b><br>"
                
                # Handle section numbering
                numbered_content = self.handle_section_numbering(section, term.sec_no)
                clause_content += numbered_content

                # Add a blank line between sections
                clause_content += "<br><br>"

                # Append the content to the contract_clauses table
                self.append('contract_clauses', {
                    'section_number': term.sec_no,
                    'clause_content': clause_content
                })

            # Update other fields
            self.has_expiry = contract_type_doc.has_expiry
            self.has_retirement = contract_type_doc.has_retirement
            self.retirement_age = contract_type_doc.retirement_age

    def handle_section_numbering(self, section, section_number):
        """Handles the numbering and formatting of sections and paragraphs."""
        content = ""
        for par in section.sec_par:
            # Construct the expected placeholder format
            placeholder_pattern = r'\{{par\."{}"\.(\d+)\}}'.format(re.escape(section.sec_head))

            # Replace placeholders with the actual section number + paragraph number
            par_num = f"{section_number}.{par.par_num}"
            formatted_text = re.sub(placeholder_pattern, f'{section_number}.\\1', par.par_text)

            content += f"{par_num}. {formatted_text}<br>"
        return content

    def generate_contract(self):
        """Generates the final contract document by replacing placeholders with actual data."""
        contract_content = ""

        for clause in self.contract_clauses:
            content = clause.clause_content

            # Replace placeholders with actual data
            content = content.replace("{employee_name}", self.employee_name or "_____________________")
            content = content.replace("{date_of_joining}", str(self.date_of_joining) or "_____________________")
            content = content.replace("{company}", self.company or "_____________________")
            content = content.replace("{employee_number}", self.employee or "_____________________")
            content = content.replace("{designation}", self.designation or "_____________________")
            content = content.replace("{current_address}", self.current_address or "_____________________")
            content = content.replace("{start_date}", str(self.start_date) or "_____________________")
            content = content.replace("{end_date}", str(self.end_date) or "_____________________")
            content = content.replace("{project}", self.project or "_____________________")
            content = content.replace("{custom_id_number}", self.custom_id_number or "_____________________")
            content = content.replace("{branch}", self.branch or "_____________________")
            content = content.replace("{contract_type}", self.contract_type or "_____________________")
            
            # Replace time placeholders with 24-hour format
            content = content.replace("{mon_start}", format_time(self.mon_start or "00:00", "HH:mm"))
            content = content.replace("{mon_end}", format_time(self.mon_end or "00:00", "HH:mm"))
            content = content.replace("{tue_start}", format_time(self.tue_start or "00:00", "HH:mm"))
            content = content.replace("{tue_end}", format_time(self.tue_end or "00:00", "HH:mm"))
            content = content.replace("{wed_start}", format_time(self.wed_start or "00:00", "HH:mm"))
            content = content.replace("{wed_end}", format_time(self.wed_end or "00:00", "HH:mm"))
            content = content.replace("{thu_start}", format_time(self.thu_start or "00:00", "HH:mm"))
            content = content.replace("{thu_end}", format_time(self.thu_end or "00:00", "HH:mm"))
            content = content.replace("{fri_start}", format_time(self.fri_start or "00:00", "HH:mm"))
            content = content.replace("{fri_end}", format_time(self.fri_end or "00:00", "HH:mm"))
            content = content.replace("{sat_start}", format_time(self.sat_start or "00:00", "HH:mm"))
            content = content.replace("{sat_end}", format_time(self.sat_end or "00:00", "HH:mm"))
            content = content.replace("{sun_start}", format_time(self.sun_start or "00:00", "HH:mm"))
            content = content.replace("{sun_end}", format_time(self.sun_end or "00:00", "HH:mm"))

            contract_content += content

        self.generated_contract = contract_content

    def notify_retirement(self):
        """Sets up a notification if the contract has a retirement clause."""
        if self.has_retirement and self.retirement_age:
            # Calculate retirement date
            retirement_date = add_years(self.date_of_birth, self.retirement_age)
            notification_date = add_months(retirement_date, -1)

            # Send notification
            self.send_notification("Retirement Notification", notification_date)

    def send_notification(self, notification_type, notification_date):
        """Sends a notification to IR Managers based on the type and date."""
        ir_managers = frappe.get_all('User', filters={
            'role_profile_name': 'IR Manager'
        })

        for manager in ir_managers:
            # Create notification logic (e.g., email or system notification)
            frappe.sendmail(
                recipients=manager.name,
                subject=f"{notification_type} for {self.employee_name}",
                message=f"This is a reminder for {notification_type} on {notification_date}."
            )