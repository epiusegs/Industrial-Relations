# Copyright (c) 2024, BuFf0k and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import today, add_days, getdate
from datetime import datetime, timedelta

def check_expiring_contracts():
    # Calculate the threshold date (4 weeks from today)
    threshold_date = (datetime.today() + timedelta(weeks=4)).strftime('%Y-%m-%d')
    
    # Fetch contracts expiring by end_date
    expiring_contracts_by_end_date = frappe.get_all("Contract of Employment", 
        filters={
            "end_date": ["<=", threshold_date]
        }, 
        fields=["name", "employee", "end_date"])

    # Get employees approaching retirement age
    employees_approaching_retirement = frappe.db.sql("""
        SELECT co.name, co.employee, co.retirement_age, e.date_of_birth
        FROM `tabContract of Employment` co
        JOIN `tabEmployee` e ON co.employee = e.name
        WHERE
            TIMESTAMPDIFF(YEAR, e.date_of_birth, %(threshold_date)s) >= co.retirement_age
    """, {
        'threshold_date': threshold_date
    }, as_dict=True)

    # Combine both lists and send notifications
    contracts_to_notify = expiring_contracts_by_end_date + employees_approaching_retirement

    for contract in contracts_to_notify:
        notify_expiry(contract)

def notify_expiry(contract):
    # Fetch all users with the "IR Manager" role
    ir_managers = frappe.get_all('Has Role', filters={'role': 'IR Manager'}, fields=['parent'])
    ir_manager_emails = [frappe.get_value('User', manager['parent'], 'email') for manager in ir_managers if frappe.get_value('User', manager['parent'], 'enabled') == 1]

    if ir_manager_emails:
        # Prepare subject and message for email
        subject = f"Contract Expiring Soon: {contract.get('employee')}"
        message = f"The contract for employee {contract.get('employee')} is expiring soon."

        # Send email to all IR Managers
        frappe.sendmail(
            recipients=ir_manager_emails,
            subject=subject,
            message=message
        )