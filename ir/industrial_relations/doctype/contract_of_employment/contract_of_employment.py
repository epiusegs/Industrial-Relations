# Copyright (c) 2024, BuFf0k and contributors
# For license information, please see license.txt

import frappe, re
from frappe.model.document import Document
from frappe.utils import add_months, add_years, format_time
from datetime import datetime
from frappe import _

def format_with_space_separator(number):
    """Formats the number with space as the thousands separator."""
    if number is None:
        return '__________'
    try:
        # Format number with comma as thousands separator first
        formatted_number = f"{number:,.2f}"
        # Replace comma with space
        formatted_number = formatted_number.replace(',', ' ')
        return formatted_number
    except (ValueError, TypeError):
        return '__________'

def number_to_words(number):
    """Convert a number into words (up to 10,000,000, including decimals)."""
    units = [
        'Zero', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine'
    ]
    teens = [
        'Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen'
    ]
    tens = [
        'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety'
    ]
    thousands = 'Thousand'
    millions = 'Million'

    def get_words_below_1000(n):
        """Convert numbers less than 1000 to words."""
        if n < 10:
            return units[n]
        elif n < 20:
            return teens[n - 10]
        elif n < 100:
            return tens[n // 10 - 2] + ('' if n % 10 == 0 else '-' + units[n % 10])
        else:
            return units[n // 100] + ' Hundred' + ('' if n % 100 == 0 else ' and ' + get_words_below_1000(n % 100))

    def get_decimal_words(decimal_part):
        """Convert the decimal part to words."""
        decimal_words = []
        for digit in decimal_part:
            decimal_words.append(units[int(digit)])
        return ' '.join(decimal_words)

    if '.' in str(number):
        integer_part, decimal_part = str(number).split('.')
        integer_part = int(integer_part)
        decimal_part = decimal_part[:2]  # Handle up to 2 decimal places
        words = number_to_words(integer_part) + ' Point ' + get_decimal_words(decimal_part)
        return words

    number = int(number)  # Handle numbers without decimals
    if number < 1000:
        return get_words_below_1000(number)
    elif number < 1000000:
        return get_words_below_1000(number // 1000) + ' ' + thousands + ('' if number % 1000 == 0 else ' ' + get_words_below_1000(number % 1000))
    elif number < 10000000:
        return get_words_below_1000(number // 1000000) + ' ' + millions + ('' if number % 1000000 == 0 else ' ' + number_to_words(number % 1000000))
    else:
        return 'Number out of range'

class ContractofEmployment(Document):
    def validate(self):
        self.update_contract_clauses()
        self.generate_contract()
        self.notify_retirement()
        
        # Ensure requied fields are populated based on selections, used for Data Import Function
        if not self.employee_name:
            self.employee_name = frappe.db.get_value('Employee', self.employee, 'employee_name')
        if not self.company:
            self.company = frappe.db.get_value('Employee', self.employee, 'company')
        if not self.designation:
            self.designation = frappe.db.get_value('Employee', self.employee, 'designation')
        if not self.current_address:
            self.current_address = frappe.db.get_value('Employee', self.employee, 'current_address')
        if not self.date_of_birth:
            self.date_of_birth = frappe.db.get_value('Employee', self.employee, 'date_of_birth')
        if not self.date_of_joining:
            self.date_of_joining = frappe.db.get_value('Employee', self.employee, 'date_of_joining')
        if not self.custom_id_number:
            self.custom_id_number = frappe.db.get_value('Employee', self.employee, 'custom_id_number')
        if not self.branch:
            self.branch = frappe.db.get_value('Employee', self.employee, 'branch')
        if not self.retirement_age:
            self.retirmenet_age = frappe.db.get_value('Contract Type', self.contract_type, 'retirement_age')
        
        # Ensure all required fields have been populated
        self.ensure_required_fields()

        # Check for allowance rate fields and set allowance descriptions
        self.set_allowance_descriptions()

    def set_allowance_descriptions(self):
        """Fetches allowance descriptions from the Contract Section linked in the remuneration field."""
        if self.remuneration:
            allowance_fields = ['allowance_1_rate', 'allowance_2_rate', 'allowance_3_rate', 'allowance_4_rate', 'allowance_5_rate']
            allowance_desc_fields = ['allowance_1_desc', 'allowance_2_desc', 'allowance_3_desc', 'allowance_4_desc', 'allowance_5_desc']

            # Check if any allowance rate is populated
            allowance_rates = {field: getattr(self, field) for field in allowance_fields if getattr(self, field)}

            if allowance_rates:
                # Fetch the Contract Section for the remuneration
                section_doc = frappe.get_doc('Contract Section', self.remuneration)

                # Initialize allowance descriptions
                allowance_descriptions = {
                    'allowance_1_desc': "",
                    'allowance_2_desc': "",
                    'allowance_3_desc': "",
                    'allowance_4_desc': "",
                    'allowance_5_desc': ""
                }

                # Iterate over the child table in the Contract Section to find matching clauses
                for row in section_doc.sec_par:
                    if row.clause_text:
                        if "{allowance_1}" in row.clause_text:
                            allowance_descriptions['allowance_1_desc'] = row.clause_text
                        elif "{allowance_2}" in row.clause_text:
                            allowance_descriptions['allowance_2_desc'] = row.clause_text
                        elif "{allowance_3}" in row.clause_text:
                            allowance_descriptions['allowance_3_desc'] = row.clause_text
                        elif "{allowance_4}" in row.clause_text:
                            allowance_descriptions['allowance_4_desc'] = row.clause_text
                        elif "{allowance_5}" in row.clause_text:
                            allowance_descriptions['allowance_5_desc'] = row.clause_text

                # Set the description fields
                for i, field in enumerate(allowance_desc_fields):
                    self.set(field, allowance_descriptions[field])

    def ensure_required_fields(self):
        """ Ensure that all fields marked as required have valid values. """
        required_fields = {
            'employee_name': 'Employee Name',
            'company': 'Company',
            'designation': 'Designation',
            'current_address': 'Current Address',
            'date_of_birth': 'Date of Birth',
            'date_of_joining': 'Date of Joining',
            'custom_id_number': 'RSA ID / Passport No.',
            'branch': 'Site',
        }
        
        missing_fields = [label for field, label in required_fields.items() if not getattr(self, field)]
        
        if missing_fields:
            frappe.throw(_("The following fields are required and missing: {0}").format(", ".join(missing_fields)))

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
            section_header = f"<b>{section.sec_head}</b><br>"

            # Handle paragraph numbering and content
            numbered_content, clause_numbers = self.handle_section_numbering(section, section_number)

            # Add the section header as an entry in the contract_clauses table
            self.append('contract_clauses', {
                'section_number': section_number,
                'clause_number': section_number,
                'clause_content': section_header
            })

            # Combine the header and content
            clause_content = section_header + numbered_content + "<br><br>"

            # Append to the contract_clauses table
            for par_num, clause_text in clause_numbers:
                self.append('contract_clauses', {
                    'section_number': section_number,
                    'clause_number': par_num,
                    'clause_content': clause_text,
                })

        # Store the mapping in self for later use
        self.sec_head_to_number = sec_head_to_number

    def handle_section_numbering(self, section, section_number):
        """Handles the numbering and formatting of sections and paragraphs."""
        content = ""
        clause_numbers = []  # To store (par_num, clause_text) tuples

        def build_par_num(par):
            """Constructs the paragraph number based on the hierarchy."""
            parts = []
            if section_number:
                parts.append(section_number)
            if par.ss_num > 0:
                parts.append(par.ss_num)
            if par.par_num > 0:
                parts.append(par.par_num)
            if par.spar_num > 0:
                parts.append(par.spar_num)
            if par.item_num > 0:
               parts.append(par.item_num)
            if par.sitem_num > 0:
                parts.append(par.sitem_num)
        
            # Join all parts with dots
            return '.'.join(map(str, parts))

        for par in section.sec_par:
            # Construct the paragraph number using the section number and paragraph number
            par_num = build_par_num(par)
            clause_text = f"{par.clause_text}<br>"

            # Append the formatted text to content
            content += clause_text

            # Append the paragraph number and text to the list
            clause_numbers.append((par_num, clause_text))

        return content, clause_numbers

    def format_date(self, date):
        """Formats the date as 'day of the week, the day of month year'."""
        if not date:
            return "_____________________"
        # Convert the date to a datetime object if it isn't already
        if isinstance(date, str):
            date = datetime.strptime(date, '%Y-%m-%d')
        # Determine the day suffix
        day_suffix = "th"
        if 4 <= date.day <= 20 or 24 <= date.day <= 30:
            day_suffix = "th"
        else:
            day_suffix = ["st", "nd", "rd"][date.day % 10 - 1]
        # Format the date
        formatted_date = date.strftime(f"%A, the {date.day}{day_suffix} of %B %Y")
        return formatted_date

    def generate_contract(self):
        """Generates the final contract document by replacing placeholders with actual data."""
        contract_content = "<table border='0' cellpadding='5' cellspacing='0'>"

        # Ensure sec_head_to_number is populated
        if not hasattr(self, 'sec_head_to_number'):
            self.update_contract_clauses()

        for clause in self.contract_clauses:
            clause_number = clause.clause_number
            clause_content = clause.clause_content

            # Format clause_number in bold
            bold_clause_number = f"<b>{clause_number}</b>"

            # Add table row with bold clause_number and clause_content
            contract_content += f"<tr><td>{bold_clause_number}</td><td>{clause_content}</td></tr>"

        contract_content += "</table>"

        # Apply replacements to the entire contract content
        replacements = {
            "{employee_name}": f"<b>{self.employee_name or '_____________________'}</b>",
            "{date_of_joining}": f"<b>{self.format_date(self.date_of_joining)}</b>",
            "{company}": f"<b>{self.company or '_____________________'}</b>",
            "{employee_number}": f"<b>{self.employee or '_____________________'}</b>",
            "{designation}": f"<b>{self.designation or '_____________________'}</b>",
            "{current_address}": f"<b>{self.current_address or '_____________________'}</b>",
            "{start_date}": f"<b>{self.format_date(self.start_date)}</b>",
            "{end_date}": f"<b>{self.format_date(self.end_date)}</b>",
            "{project}": f"<b>{self.project or '_____________________'}</b>",
            "{custom_id_number}": f"<b>{self.custom_id_number or '_____________________'}</b>",
            "{branch}": f"<b>{self.branch or '_____________________'}</b>",
            "{contract_type}": f"<b>{self.contract_type or '_____________________'}</b>",
            "{restraint_period}": f"<b>{self.restraint_period or '_____________________'}</b>",
            "{restraint_territory}": f"<b>{self.restraint_territory or '_____________________'}</b>",
            "{mon_start}": f"<b>{format_time(self.mon_start or '00:00', 'HH:mm')}</b>",
            "{mon_end}": f"<b>{format_time(self.mon_end or '00:00', 'HH:mm')}</b>",
            "{tue_start}": f"<b>{format_time(self.tue_start or '00:00', 'HH:mm')}</b>",
            "{tue_end}": f"<b>{format_time(self.tue_end or '00:00', 'HH:mm')}</b>",
            "{wed_start}": f"<b>{format_time(self.wed_start or '00:00', 'HH:mm')}</b>",
            "{wed_end}": f"<b>{format_time(self.wed_end or '00:00', 'HH:mm')}</b>",
            "{thu_start}": f"<b>{format_time(self.thu_start or '00:00', 'HH:mm')}</b>",
            "{thu_end}": f"<b>{format_time(self.thu_end or '00:00', 'HH:mm')}</b>",
            "{fri_start}": f"<b>{format_time(self.fri_start or '00:00', 'HH:mm')}</b>",
            "{fri_end}": f"<b>{format_time(self.fri_end or '00:00', 'HH:mm')}</b>",
            "{sat_start}": f"<b>{format_time(self.sat_start or '00:00', 'HH:mm')}</b>",
            "{sat_end}": f"<b>{format_time(self.sat_end or '00:00', 'HH:mm')}</b>",
            "{sun_start}": f"<b>{format_time(self.sun_start or '00:00', 'HH:mm')}</b>",
            "{sun_end}": f"<b>{format_time(self.sun_end or '00:00', 'HH:mm')}</b>",
            "{rate}": f"<b>{format_with_space_separator(self.rate) + ' (' + number_to_words(self.rate) + ')' if self.rate else '__________'}</b>",
            "{allowance_1}": f"<b>{format_with_space_separator(self.allowance_1_rate) + ' (' + number_to_words(self.allowance_1_rate) + ')'  if self.allowance_1_rate else '__________'}</b>",
            "{allowance_2}": f"<b>{format_with_space_separator(self.allowance_2_rate) + ' (' + number_to_words(self.allowance_2_rate) + ')'  if self.allowance_2_rate else '__________'}</b>",
            "{allowance_3}": f"<b>{format_with_space_separator(self.allowance_3_rate) + ' (' + number_to_words(self.allowance_3_rate) + ')'  if self.allowance_3_rate else '__________'}</b>",
            "{allowance_4}": f"<b>{format_with_space_separator(self.allowance_4_rate) + ' (' + number_to_words(self.allowance_4_rate) + ')'  if self.allowance_4_rate else '__________'}</b>",
            "{allowance_5}": f"<b>{format_with_space_separator(self.allowance_5_rate) + ' (' + number_to_words(self.allowance_5_rate) + ')'  if self.allowance_5_rate else '__________'}</b>",
            "{retirement_age}": f"<b>{str(self.retirement_age) + ' (' + number_to_words(self.retirement_age) + ')' if self.retirement_age is not None else '__________'}</b>"
        }

        # Apply replacements to the contract content
        for placeholder, replacement in replacements.items():
            contract_content = contract_content.replace(placeholder, replacement)

        # Replace section headings with section numbers
        for sec_head, section_number in self.sec_head_to_number.items():
            escaped_sec_head = re.escape(sec_head)
            pattern = rf'\{{par\."{escaped_sec_head}"\}}'
            contract_content = re.sub(pattern, str(section_number), contract_content)

        # Apply text formatting
        contract_content = re.sub(r'//(.*?)//', r'<i>\1</i>', contract_content)  # Italic
        contract_content = re.sub(r'__(.*?)__', r'<u>\1</u>', contract_content)  # Underline
        contract_content = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', contract_content)  # Bold

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

    def before_submit(self):
        if not self.signed_contract:
            frappe.throw(_("You cannot submit the document without attaching the signed contract."))