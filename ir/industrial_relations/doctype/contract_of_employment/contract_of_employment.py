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
        if not self.contract_type:
            return

        contract_type_doc = frappe.get_doc('Contract Type', self.contract_type)
        self.contract_clauses = []  # Clear existing clauses

        # Dictionary to map section heading to section number
        sec_head_to_number = {}

        # Fetch the names of the specific sections for comparison
        remuneration_section_name = frappe.db.get_value('Contract Section', {'sec_head': 'Remuneration'}, 'name')
        working_hours_section_name = frappe.db.get_value('Contract Section', {'sec_head': 'Working Hours'}, 'name')

        for term in contract_type_doc.contract_terms:
            # Determine which section to use
            if term.section == remuneration_section_name and self.remuneration:
                section = frappe.get_doc('Contract Section', self.remuneration)
            elif term.section == working_hours_section_name and self.working_hours:
                section = frappe.get_doc('Contract Section', self.working_hours)
            else:
                section = frappe.get_doc('Contract Section', term.section)

            # Map section heading to section number
            sec_head_to_number[section.sec_head] = term.sec_no

            # Numbered section header
            section_number = term.sec_no
            section_header = f"<b>{section_number}. {section.sec_head}</b><br>"

            # Handle paragraph numbering and content
            numbered_content = self.handle_section_numbering(section, section_number)

            # Combine the header and content
            clause_content = section_header + numbered_content + "<br><br>"

            # Append to the contract_clauses table
            self.append('contract_clauses', {
                'section_number': section_number,
                'clause_content': clause_content
            })

            # Store the mapping in self for later use
            self.sec_head_to_number = sec_head_to_number

    def handle_section_numbering(self, section, section_number):
        """Handles the numbering and formatting of sections and paragraphs."""
        content = ""
        for par in section.sec_par:
            # Construct the paragraph number using the section number and paragraph number
            par_num = f"{section_number}.{par.par_num}"

            # Append the formatted text to content
            content += f"{par_num}. {par.par_text}<br>"

        return content

    def generate_contract(self):
        """Generates the final contract document by replacing placeholders with actual data."""
        contract_content = ""

        # Ensure sec_head_to_number is populated
        if not hasattr(self, 'sec_head_to_number'):
            self.update_contract_clauses()

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
            content = content.replace("{rate}", "{:.2f}".format(self.rate) if self.rate else "__________")
            content = content.replace("{retirement_age}", str(self.retirement_age) or "__________")
            content = content.replace("{restraint_period}", self.restraint_period or "_____________________")
            content = content.replace("{restraint_territory}", self.restraint_territory or "_____________________")
            
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

            # Replace section headings with section numbers
            for sec_head, section_number in self.sec_head_to_number.items():
                pattern = rf'\{{par\."{sec_head}"\}}'
                content = re.sub(pattern, str(section_number), content)

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
