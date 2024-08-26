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

        # Clear existing clauses
        self.contract_clauses = []

        # Fetch the Contract Type document
        contract_type_doc = frappe.get_doc('Contract Type', self.contract_type)

        # Dictionary to map section heading to section number
        sec_head_to_number = {}

        # Loop through contract terms in the contract type document
        for term in contract_type_doc.contract_terms:
            # Determine which section to use
            if term.section == "Remuneration Placeholder":
                section = frappe.get_doc('Contract Section', self.remuneration)
            elif term.section == "Working Hours Placeholder":
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

            # Replace placeholders with field data in bold
            content = content.replace("{employee_name}", f"<b>{self.employee_name or '_____________________'}</b>")
            content = content.replace("{date_of_joining}", f"<b>{str(self.date_of_joining) or '_____________________'}</b>")
            content = content.replace("{company}", f"<b>{self.company or '_____________________'}</b>")
            content = content.replace("{employee_number}", f"<b>{self.employee or '_____________________'}</b>")
            content = content.replace("{designation}", f"<b>{self.designation or '_____________________'}</b>")
            content = content.replace("{current_address}", f"<b>{self.current_address or '_____________________'}</b>")
            content = content.replace("{start_date}", f"<b>{str(self.start_date) or '_____________________'}</b>")
            content = content.replace("{end_date}", f"<b>{str(self.end_date) or '_____________________'}</b>")
            content = content.replace("{project}", f"<b>{self.project or '_____________________'}</b>")
            content = content.replace("{custom_id_number}", f"<b>{self.custom_id_number or '_____________________'}</b>")
            content = content.replace("{branch}", f"<b>{self.branch or '_____________________'}</b>")
            content = content.replace("{contract_type}", f"<b>{self.contract_type or '_____________________'}</b>")
            content = content.replace("{rate}", f"<b>{'{:.2f}'.format(self.rate) if self.rate else '__________'}</b>")
            content = content.replace("{retirement_age}", f"<b>{str(self.retirement_age) or '__________'}</b>")
            content = content.replace("{restraint_period}", f"<b>{self.restraint_period or '_____________________'}</b>")
            content = content.replace("{restraint_territory}", f"<b>{self.restraint_territory or '_____________________'}</b>")
            content = content.replace("{mon_start}", f"<b>{format_time(self.mon_start or '00:00', 'HH:mm')}</b>")
            content = content.replace("{mon_end}", f"<b>{format_time(self.mon_end or '00:00', 'HH:mm')}</b>")
            content = content.replace("{tue_start}", f"<b>{format_time(self.tue_start or '00:00', 'HH:mm')}</b>")
            content = content.replace("{tue_end}", f"<b>{format_time(self.tue_end or '00:00', 'HH:mm')}</b>")
            content = content.replace("{wed_start}", f"<b>{format_time(self.wed_start or '00:00', 'HH:mm')}</b>")
            content = content.replace("{wed_end}", f"<b>{format_time(self.wed_end or '00:00', 'HH:mm')}</b>")
            content = content.replace("{thu_start}", f"<b>{format_time(self.thu_start or '00:00', 'HH:mm')}</b>")
            content = content.replace("{thu_end}", f"<b>{format_time(self.thu_end or '00:00', 'HH:mm')}</b>")
            content = content.replace("{fri_start}", f"<b>{format_time(self.fri_start or '00:00', 'HH:mm')}</b>")
            content = content.replace("{fri_end}", f"<b>{format_time(self.fri_end or '00:00', 'HH:mm')}</b>")
            content = content.replace("{sat_start}", f"<b>{format_time(self.sat_start or '00:00', 'HH:mm')}</b>")
            content = content.replace("{sat_end}", f"<b>{format_time(self.sat_end or '00:00', 'HH:mm')}</b>")
            content = content.replace("{sun_start}", f"<b>{format_time(self.sun_start or '00:00', 'HH:mm')}</b>")
            content = content.replace("{sun_end}", f"<b>{format_time(self.sun_end or '00:00', 'HH:mm')}</b>")

            # Replace section headings with section numbers
            for sec_head, section_number in self.sec_head_to_number.items():
                # Escape any special characters in sec_head
                escaped_sec_head = re.escape(sec_head)
                pattern = rf'\{{par\."{escaped_sec_head}"\}}'
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
